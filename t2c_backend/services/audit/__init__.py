import io
from datetime import datetime

from babel.dates import format_date
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import joinedload

from t2c_backend.core.i18n import _
from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Asset, AssetType, Audit, AuditTask, AuditTaskDocument
from t2c_backend.schemas.v1.audit import (
    AssetAuditResponse,
    CreateAudit,
    CreateAuditTask,
)
from t2c_backend.schemas.v1.audit import (
    AuditTaskDocument as AuditTaskDocumentSchema,
)
from t2c_backend.utils.enums import AuditTaskStatus, Language, SortBy
from t2c_backend.utils.errors import BadRequestError, NotFoundError


class AuditService:
    _model = Audit

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.task_repository = BaseRepository(app, session, AuditTask)
        self.task_document_repository = BaseRepository(app, session, AuditTaskDocument)

    async def create_audit_task(
        self, organization_id: int, task: CreateAuditTask, documents: list[UploadFile] = None
    ):
        audit_task = await self.task_repository.save(
            AuditTask(
                task_name=task.task_name,
                status=AuditTaskStatus(task.status),
            )
        )

        saved_documents = []

        for document in documents if documents is not None else []:
            saved_document = await self.app.clients.storage.save_audit_task_document(
                organization_id, audit_task.id, document
            )
            saved_documents.append(
                await self.task_document_repository.save(
                    AuditTaskDocument(
                        name=saved_document.filename,
                        content_type=saved_document.content_type,
                        audit_task_id=audit_task.id,
                    )
                )
            )

        return audit_task, saved_documents

    async def create_audit(
        self,
        asset_id: int,
        audit_data: CreateAudit,
        audit_task_data: list[AuditTask],
        user_id: int,
    ):
        asset = await self.app.services.asset_service.repository.exists(id=asset_id)
        if not asset:
            raise NotFoundError("Asset not found")

        if not audit_task_data or len(audit_task_data) == 0:
            raise BadRequestError("Audit task is required.")

        audit = await self.repository.save(
            Audit(
                inspection_date=datetime.fromtimestamp(audit_data.inspection_date),
                valid_until=datetime.fromtimestamp(audit_data.valid_until),
                asset_id=asset_id,
                user_id=user_id,
            )
        )

        audit_tasks = []
        for audit_task in audit_task_data:
            audit_task.audit_id = audit.id
            documents = []

            if audit_task.documents:
                for document in audit_task.documents:
                    document = AuditTaskDocumentSchema.to_orm(document)
                    await self.task_repository.session.merge(document)
                    documents.append(document)

            await self.repository.session.merge(audit_task)
            audit_tasks.append(audit_task)

        return audit, audit_tasks

    async def get_audit_list(
        self,
        q: str | None,
        page: int,
        page_size: int,
        location_id: int,
        sort_by: SortBy | None,
        inspection_start_date: datetime.date = None,
        inspection_end_date: datetime.date = None,
        valid_until_start_date: datetime.date = None,
        valid_until_end_date: datetime.date = None,
        is_audit_available: bool = None,
    ):
        model = Asset
        sort_order = {
            SortBy.Latest: desc(model.created_at),
            SortBy.Oldest: asc(model.created_at),
        }

        asset_filters = []
        audit_filters = []

        if inspection_start_date and inspection_end_date:
            filters = self._model.inspection_date.between(
                inspection_start_date, inspection_end_date
            )
            audit_filters.append(filters)
            asset_filters.append(model.audit.any(filters))

        if valid_until_start_date and valid_until_end_date:
            filters = self._model.valid_until.between(valid_until_start_date, valid_until_end_date)
            audit_filters.append(filters)
            asset_filters.append(model.audit.any(filters))

        if is_audit_available:
            asset_filters.append(model.audit.any())

        if q:
            serial_no_filter = BaseRepository.parse_filters(model, serial_no__ilike=f"%{q}%")
            asset_type_name_filter = BaseRepository.parse_filters(AssetType, name__ilike=f"%{q}%")
            asset_filters.append(
                or_(
                    *serial_no_filter,
                    *[model.asset_type.has(condition) for condition in asset_type_name_filter],
                )
            )

        select_query = (
            select(model)
            .options(
                joinedload(model.audit),
                joinedload(model.audit).joinedload(self._model.audit_tasks),
                joinedload(model.audit)
                .joinedload(self._model.audit_tasks)
                .joinedload(AuditTask.documents),
                joinedload(model.asset_type),
                joinedload(model.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(model.audit.and_(*audit_filters) if audit_filters else model.audit),
            )
            .order_by(sort_order[sort_by])
            .filter(*asset_filters)
            .filter(model.location_id == location_id)
        )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_data: [
                AssetAuditResponse.from_model(asset) for asset in asset_data
            ],
        )

    async def delete_audit(self, audit_id: int, location_id: int):
        audit = await self.repository.get_one_or_none(id=audit_id)

        if not audit:
            raise NotFoundError("Audit not found")

        asset = await self.app.services.asset_service.repository.exists(
            id=audit.asset_id, location_id=location_id
        )

        if not asset:
            raise NotFoundError("Audit not found")

        await self.repository.delete(id=audit.id)

    async def delete_audit_task(self, audit_task_id: int):
        audit_task = await self.task_repository.get_one_or_none(id=audit_task_id)

        if not audit_task:
            raise NotFoundError("Audit task not found")

        await self.task_repository.delete(id=audit_task.id)
        await self.task_document_repository.delete(audit_task_id=audit_task.id)

    async def document_get_download(
        self, organization_id, audit_id: int, task_id: int, document_id: str
    ):
        audit = await self.repository.get_one_or_none(id=audit_id)
        if not audit:
            raise NotFoundError("Document not found")

        task = await self.task_repository.get_one_or_none(id=task_id, audit_id=audit.id)
        if not task:
            raise NotFoundError("Document not found")

        document = await self.task_document_repository.get_one_or_none(
            id=document_id, task_id=task.id
        )
        if not document:
            raise NotFoundError("Document not found")

        return StreamingResponse(
            self.app.clients.storage.get_audit_task_document(
                organization_id, task.id, document.name
            ),
            media_type=document.content_type,
        )

    async def get_audit_report(self, asset_id: int, audit_id: int, language: Language):
        asset = await self.app.services.asset_service.repository.get_one_or_none(
            id=asset_id,
            options=[
                joinedload(Asset.asset_type),
                joinedload(Asset.asset_type).joinedload(AssetType.asset_type_category),
            ],
        )
        if not asset:
            raise NotFoundError("Asset not found")

        audit = await self.repository.get_one_or_none(
            id=audit_id,
            asset_id=asset.id,
            options=[
                joinedload(self._model.audit_tasks),
                joinedload(self._model.audit_tasks).joinedload(AuditTask.documents),
            ],
        )
        if not audit:
            raise NotFoundError("Audit not found")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter, topMargin=70, leftMargin=40, rightMargin=40
        )
        elements = []
        styles = getSampleStyleSheet()

        normal_bigger = ParagraphStyle(
            name="NormalBigger", parent=styles["Normal"], fontSize=11, leading=14
        )
        green_bold = ParagraphStyle(
            "GreenBold", parent=styles["Normal"], textColor=colors.green, fontSize=11, leading=14
        )
        red_bold = ParagraphStyle(
            "RedBold", parent=styles["Normal"], textColor=colors.red, fontSize=11, leading=14
        )

        asset_info_data = [
            [Paragraph(f"<b>{_('Asset Details:')}</b>", styles["Heading4"])],
            [
                Paragraph(
                    f"<b>{_('Manufacturing Date:')}</b> "
                    f"{
                        format_date(
                            asset.manufacturing_date.date(),
                            format='long',
                            locale=Language(language).value,
                        )
                    }",
                    normal_bigger,
                )
            ],
        ]
        if asset.serial_no:
            asset_info_data.append(
                [Paragraph(f"<b>{_('Serial Number:')}</b> {asset.serial_no}", normal_bigger)]
            )
        asset_info_data.append(
            [Paragraph(f"<b>{_('Asset Type:')}</b> {asset.asset_type.name}", normal_bigger)]
        )
        asset_info_data.append(
            [
                Paragraph(
                    f"<b>{_('Asset Type Category:')}</b> "
                    f"{asset.asset_type.asset_type_category.name}",
                    normal_bigger,
                )
            ]
        )
        asset_table = Table(asset_info_data, colWidths=[590])
        asset_table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        elements.append(asset_table)
        elements.append(Spacer(1, 0.3 * inch))

        data = [
            [
                "#",
                _("Task Name"),
                _("Status"),
                _("Inspection Date"),
                _("Valid Until"),
                _("Documents"),
            ]
        ]
        for index, task in enumerate(audit.audit_tasks):
            if task.status == AuditTaskStatus.SUCCEEDED:
                status_para = Paragraph(
                    f"{_(AuditTaskStatus(task.status).value)}", style=green_bold
                )
            else:
                status_para = Paragraph(f"{_(AuditTaskStatus(task.status).value)}", style=red_bold)

            if task.documents:
                bullet_docs = "<br/>".join([f"&bull; {doc.name}" for doc in task.documents])
            else:
                bullet_docs = "N/A"

            data.append(
                [
                    index + 1,
                    task.task_name,
                    status_para,
                    format_date(
                        audit.inspection_date.date(), format="long", locale=Language(language).value
                    ),
                    format_date(audit.valid_until, format="long", locale=Language(language).value),
                    Paragraph(bullet_docs, style=normal_bigger),
                ]
            )

        column_widths = [30, 100, 90, 100, 100, 180]
        table = Table(data, colWidths=column_widths, repeatRows=1)

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.floralwhite),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("ALIGN", (1, 1), (1, -1), "LEFT"),
                    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(table)

        def draw_header(canvas: Canvas, doc):
            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawCentredString(
                letter[0] / 2,
                letter[1] - 40,
                f"{_('Audit Report for')} "
                f"{
                    format_date(
                        audit.inspection_date.date(), format='long', locale=Language(language).value
                    )
                }",
            )

        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)

        buffer.seek(0)
        filename = f"audit_report_{
            format_date(
                audit.inspection_date.date(), format='long', locale=Language(language).value
            )
        }.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(AuditService(app, session), session.info["session_id"])
