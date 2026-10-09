import io
import uuid
from datetime import UTC, datetime, tzinfo
from urllib.parse import quote, urljoin
from xml.sax.saxutils import escape

from babel.dates import format_date
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from reportlab.graphics.shapes import Drawing, Polygon, PolyLine
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import and_, asc, desc, or_, select
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
from t2c_backend.utils.enums import AuditTaskStatus, DocumentFor, Language, SortBy, TaskType
from t2c_backend.utils.errors import BadRequestError, NotFoundError
from t2c_backend.utils.misc import datetime_from_epoch

PAGE = A4
MARGIN = 36
HEADER_HEIGHT = 64
CONTENT_WIDTH = PAGE[0] - 2 * MARGIN

# Matches the frontend theme (frontend/src/theme-config.ts and its grey scale).
INK = colors.HexColor("#1C252E")
MUTED = colors.HexColor("#637381")
BORDER = colors.HexColor("#DFE3E8")
SURFACE = colors.HexColor("#F9FAFB")
NEUTRAL = colors.HexColor("#F0F0F0")
BRAND = colors.HexColor("#AFCB08")
BRAND_DARK = colors.HexColor("#333333")

# (text colour, background) per task status: the frontend's soft label, its `dark`
# shade on `main` at 16% opacity over white.
STATUS_COLORS = {
    AuditTaskStatus.PASSED: (colors.HexColor("#118D57"), colors.HexColor("#DCF6E5")),
    AuditTaskStatus.CONDITIONAL: (colors.HexColor("#B76E00"), colors.HexColor("#FFF2D6")),
    AuditTaskStatus.FAILED: (colors.HexColor("#B71D18"), colors.HexColor("#FFE4DE")),
}

BODY = ParagraphStyle("AuditBody", fontName="Helvetica", fontSize=9.5, leading=13, textColor=INK)
STRONG = ParagraphStyle("AuditStrong", parent=BODY, fontName="Helvetica-Bold")
SMALL = ParagraphStyle("AuditSmall", parent=BODY, fontSize=8, leading=11, textColor=MUTED)
LABEL = ParagraphStyle("AuditLabel", parent=SMALL, fontName="Helvetica-Bold")
VALUE = ParagraphStyle("AuditValue", parent=STRONG, fontSize=11, leading=15)
SECTION = ParagraphStyle(
    "AuditSection", parent=STRONG, fontSize=12, leading=16, spaceBefore=18, spaceAfter=8
)
TABLE_HEAD = ParagraphStyle("AuditTableHead", parent=LABEL, textColor=MUTED)
LINK = colors.HexColor("#0B5CAD")


def _file_icon() -> Drawing:
    """A page outline with a folded corner, sized to sit beside a line of body text."""
    icon = Drawing(9, 11)
    style = {"strokeColor": MUTED, "strokeWidth": 0.8, "strokeLineJoin": 1}
    icon.add(Polygon([0.5, 0.5, 8.5, 0.5, 8.5, 7.5, 5.5, 10.5, 0.5, 10.5], fillColor=None, **style))
    icon.add(PolyLine([5.5, 10.5, 5.5, 7.5, 8.5, 7.5], **style))
    return icon


def _document_name(name: str, url: str) -> Paragraph:
    href = escape(url, {'"': "&quot;"})
    return Paragraph(f'<a href="{href}" color="{LINK.hexval()}"><u>{escape(name)}</u></a>', BODY)


def _documents(documents, link) -> Table:
    rows = [[_file_icon(), _document_name(doc.name, link(doc))] for doc in documents]
    table = Table(rows, colWidths=[14, None], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (0, -1), 1.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (1, 0), (1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _pill(text: str, status: AuditTaskStatus) -> Table:
    fg, bg = STATUS_COLORS[status]
    style = ParagraphStyle("AuditPill", parent=LABEL, textColor=fg, alignment=1)
    text = text.upper()
    width = stringWidth(text, style.fontName, style.fontSize) + 18
    pill = Table([[Paragraph(text, style)]], colWidths=[width], hAlign="LEFT")
    pill.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return pill


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
        seen = set()
        duplicates = set()
        for document in documents:
            if document.filename in seen:
                duplicates.add(document.filename)
            seen.add(document.filename)
        if duplicates:
            raise BadRequestError(f"Documents uploaded more than once: {','.join(duplicates)}")

        audit_task = await self.task_repository.save(
            AuditTask(
                task_name=task.task_name,
                task_type=TaskType(task.task_type),
                status=AuditTaskStatus(task.status),
                performed_by_org=task.performed_by_org,
                role_of_org=task.role_of_org,
                first_name=task.first_name,
                last_name=task.last_name,
            )
        )

        saved_documents = []

        for document in documents:
            saved_document = await self.app.clients.storage.save_document(
                organization_id=organization_id,
                document_for=DocumentFor.AuditTaskDocuments,
                file_id=audit_task.id,
                file=document,
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
                inspection_date=datetime_from_epoch(audit_data.inspection_date),
                valid_until=datetime_from_epoch(audit_data.valid_until),
                asset_id=asset_id,
                user_id=user_id,
            )
        )

        audit_tasks = []
        for audit_task in audit_task_data:
            if not await self.task_repository.exists(id=audit_task.id):
                raise BadRequestError(f"Audit task {audit_task.task_name} not found.")
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
        inspection_start_date: int | None = None,
        inspection_end_date: int | None = None,
        valid_until_start_date: int | None = None,
        valid_until_end_date: int | None = None,
        task_type: TaskType | None = None,
        task_status: list[AuditTaskStatus] | None = None,
    ):
        model = Asset
        sort_order = {
            SortBy.Latest: desc(model.created_at),
            SortBy.Oldest: asc(model.created_at),
        }

        asset_filters = []
        audit_filters = []

        if inspection_start_date is not None and inspection_end_date is not None:
            audit_filters.append(
                self._model.inspection_date.between(
                    datetime_from_epoch(inspection_start_date),
                    datetime_from_epoch(inspection_end_date),
                )
            )

        if valid_until_start_date is not None and valid_until_end_date is not None:
            audit_filters.append(
                self._model.valid_until.between(
                    datetime_from_epoch(valid_until_start_date),
                    datetime_from_epoch(valid_until_end_date),
                )
            )

        # A single task must match every task filter, and only matching tasks are loaded.
        audit_task_filters = []
        if task_type:
            audit_task_filters.append(AuditTask.task_type == task_type)
        if task_status:
            audit_task_filters.append(AuditTask.status.in_(task_status))

        if audit_task_filters:
            audit_filters.append(self._model.audit_tasks.any(and_(*audit_task_filters)))

        # A single audit must match every audit filter, and only matching audits are loaded.
        if audit_filters:
            asset_filters.append(model.audit.any(and_(*audit_filters)))

        if q:
            serial_no_filter = BaseRepository.parse_filters(model, serial_no__ilike=f"%{q}%")
            asset_type_name_filter = BaseRepository.parse_filters(AssetType, name__ilike=f"%{q}%")
            task_name_filter = BaseRepository.parse_filters(AuditTask, task_name__ilike=f"%{q}%")
            asset_search = or_(
                *serial_no_filter,
                *[model.asset_type.has(condition) for condition in asset_type_name_filter],
            )
            task_name_match = self._model.audit_tasks.any(
                and_(*task_name_filter, *audit_task_filters)
            )
            asset_filters.append(
                or_(asset_search, model.audit.any(and_(*audit_filters, task_name_match)))
            )
            # Unless the asset itself matched the search, only audits and tasks whose task name
            # matched are loaded.
            audit_filters.append(or_(asset_search, task_name_match))
            audit_task_filters.append(or_(asset_search, *task_name_filter))

        audit_relationship = model.audit.and_(*audit_filters) if audit_filters else model.audit
        audit_task_relationship = (
            self._model.audit_tasks.and_(*audit_task_filters)
            if audit_task_filters
            else self._model.audit_tasks
        )

        select_query = (
            select(model)
            .options(
                joinedload(audit_relationship)
                .joinedload(audit_task_relationship)
                .joinedload(AuditTask.documents),
                joinedload(model.asset_type),
                joinedload(model.asset_type).joinedload(AssetType.asset_type_category),
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

    async def delete_audit(self, audit_id: int, location_id: int, organization_id: int):
        audit = await self.repository.get_one_or_none(
            id=audit_id,
            join=[self._model.asset],
            where=[Asset.location_id == location_id],
            options=[
                joinedload(Audit.audit_tasks),
                joinedload(Audit.audit_tasks).joinedload(AuditTask.documents),
            ],
        )

        if not audit:
            raise NotFoundError("Audit not found")

        await self.repository.delete(id=audit.id)

        for audit_task in audit.audit_tasks:
            for document in audit_task.documents:
                await self.app.clients.storage.delete_document(
                    organization_id=organization_id,
                    document_for=DocumentFor.AuditTaskDocuments,
                    file_id=audit_task.id,
                    filename=document.name,
                )

    async def delete_audit_task(self, audit_task_id: int, organization_id: int):
        audit_task = await self.task_repository.get_one_or_none(
            id=audit_task_id, options=[joinedload(AuditTask.documents)]
        )

        if not audit_task:
            raise NotFoundError("Audit task not found")

        await self.task_repository.delete(id=audit_task.id)
        await self.task_document_repository.delete(audit_task_id=audit_task.id)

        for document in audit_task.documents:
            await self.app.clients.storage.delete_document(
                organization_id=organization_id,
                document_for=DocumentFor.AuditTaskDocuments,
                file_id=audit_task.id,
                filename=document.name,
            )

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
            id=document_id, audit_task_id=task.id
        )
        if not document:
            raise NotFoundError("Document not found")

        return StreamingResponse(
            self.app.clients.storage.get_document(
                organization_id=organization_id,
                document_for=DocumentFor.AuditTaskDocuments,
                file_id=task.id,
                file_name=document.name,
            ),
            media_type=document.content_type,
        )

    def _document_link(self, document: AuditTaskDocument) -> str:
        return urljoin(
            str(self.app.config.BACKEND_URL),
            f"{self.app.config.API_STR}/v1/public/audit-document/{document.id}/download",
        )

    async def public_document_download(self, document_id: uuid.UUID):
        document = await self.task_document_repository.get_one_or_none(
            id=document_id,
            options=[
                joinedload(AuditTaskDocument.audit_task)
                .joinedload(AuditTask.audit)
                .joinedload(Audit.asset)
                .joinedload(Asset.location)
            ],
        )
        if not document or not document.audit_task.audit:
            raise NotFoundError("Document not found")

        return StreamingResponse(
            self.app.clients.storage.get_document(
                organization_id=document.audit_task.audit.asset.location.organization_id,
                document_for=DocumentFor.AuditTaskDocuments,
                file_id=document.audit_task_id,
                file_name=document.name,
            ),
            media_type=document.content_type,
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(document.name)}"},
        )

    async def get_audit_report(
        self, asset_id: int, audit_id: int, language: Language, timezone: tzinfo = UTC
    ):
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

        locale = Language(language).value

        def date(value: datetime) -> str:
            # Stored values are UTC; show the calendar day as the requester sees it.
            return format_date(value.astimezone(timezone).date(), format="long", locale=locale)

        status_labels = {
            AuditTaskStatus.PASSED: _("Passed"),
            AuditTaskStatus.CONDITIONAL: _("Conditional"),
            AuditTaskStatus.FAILED: _("Failed"),
        }
        type_labels = {TaskType.audit: _("Audit"), TaskType.inspection: _("Inspection")}

        tasks = audit.audit_tasks
        statuses = [AuditTaskStatus(task.status) for task in tasks]
        inspection_date = date(audit.inspection_date)
        generated_on = date(datetime.now(UTC))

        # Summary cards
        counts = ", ".join(
            f"{statuses.count(status)} {status_labels[status].lower()}"
            for status in STATUS_COLORS
            if statuses.count(status)
        )
        cards = [
            (_("Inspection Date"), inspection_date),
            (_("Valid Until"), date(audit.valid_until)),
            (_("Tasks"), f"{len(tasks)}", counts),
        ]
        # Cards alternate with empty gap columns so each can have its own box.
        gap = 10
        card_width = (CONTENT_WIDTH - gap * (len(cards) - 1)) / len(cards)
        row, widths = [], []
        for label, value, *note in cards:
            cell = [Paragraph(escape(label).upper(), LABEL), Spacer(1, 6)]
            cell.append(Paragraph(escape(value), VALUE))
            if note and note[0]:
                cell.append(Paragraph(escape(note[0]), SMALL))
            row += [cell, ""]
            widths += [card_width, gap]
        summary = Table([row[:-1]], colWidths=widths[:-1])
        summary_style = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]
        for i in range(0, len(cards) * 2, 2):
            summary_style += [
                ("BACKGROUND", (i, 0), (i, 0), SURFACE),
                ("BOX", (i, 0), (i, 0), 0.75, BORDER),
            ]
        summary.setStyle(TableStyle(summary_style))

        # Asset details: label/value pairs, two per row
        details = [
            (_("Asset Type"), asset.asset_type.name),
            (_("Asset Type Category"), asset.asset_type.asset_type_category.name),
            (_("Serial Number"), asset.serial_no),
            (_("Manufacturing Date"), date(asset.manufacturing_date)),
            (_("Pass ID"), asset.pass_id),
            (_("Economic Operator"), asset.economic_operator),
        ]
        details = [(label, value) for label, value in details if value]
        rows = []
        for i in range(0, len(details), 2):
            row = []
            for label, value in details[i : i + 2]:
                row += [Paragraph(escape(label), SMALL), Paragraph(escape(str(value)), STRONG)]
            rows.append(row + [""] * (4 - len(row)))
        label_width, value_width = 95, CONTENT_WIDTH / 2 - 95
        asset_table = Table(rows, colWidths=[label_width, value_width] * 2)
        asset_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        # Tasks
        elements = [
            summary,
            Paragraph(escape(_("Asset Details")), SECTION),
            asset_table,
            Paragraph(escape(_("Tasks")), SECTION),
        ]
        if tasks:
            headers = ["#", _("Task"), _("Status"), _("Performed By"), _("Documents")]
            data = [[Paragraph(escape(h).upper(), TABLE_HEAD) for h in headers]]
            for index, task in enumerate(tasks, start=1):
                performer = " · ".join(
                    escape(part) for part in (task.role_of_org, task.performed_by_org) if part
                )
                data.append(
                    [
                        Paragraph(str(index), SMALL),
                        [
                            Paragraph(escape(task.task_name), STRONG),
                            Paragraph(type_labels.get(TaskType(task.task_type), ""), SMALL),
                        ],
                        _pill(status_labels[AuditTaskStatus(task.status)], task.status),
                        [
                            Paragraph(escape(task.get_full_name()), BODY),
                            Paragraph(performer, SMALL),
                        ],
                        _documents(task.documents, self._document_link)
                        if task.documents
                        else Paragraph("—", SMALL),
                    ]
                )
            task_table = Table(data, colWidths=[26, 140, 110, 127, 120], repeatRows=1)
            task_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), NEUTRAL),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SURFACE]),
                        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER),
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("LEFTPADDING", (0, 0), (0, -1), 4),
                        ("RIGHTPADDING", (0, 0), (0, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            elements.append(task_table)
        else:
            elements.append(Paragraph(escape(_("No tasks were recorded for this audit.")), SMALL))

        title = _("Audit Report")
        subtitle = f"{asset.asset_type.name} · {inspection_date}"
        footer = f"{_('Generated on')} {generated_on}"
        page_label = _("Page {page} of {total}")

        class ReportCanvas(Canvas):
            """Draws header and footer once every page is known, so the footer can say 'of N'."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._pages = []

            def showPage(self):  # noqa: N802 — ReportLab API name
                self._pages.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                for number, state in enumerate(self._pages, start=1):
                    self.__dict__.update(state)
                    self._decorate(number, len(self._pages))
                    super().showPage()
                super().save()

            def _decorate(self, number: int, total: int):
                width, height = PAGE
                self.setFillColor(BRAND_DARK)
                self.rect(0, height - HEADER_HEIGHT, width, HEADER_HEIGHT, stroke=0, fill=1)
                self.setFillColor(BRAND)
                self.rect(0, height - HEADER_HEIGHT - 4, width, 4, stroke=0, fill=1)
                self.setFillColor(colors.white)
                self.setFont("Helvetica-Bold", 18)
                self.drawString(MARGIN, height - 32, title)
                self.setFont("Helvetica", 10)
                self.setFillColor(colors.HexColor("#ABABAB"))
                self.drawString(MARGIN, height - 49, subtitle)

                self.setStrokeColor(BORDER)
                self.setLineWidth(0.5)
                self.line(MARGIN, 30, width - MARGIN, 30)
                self.setFont("Helvetica", 8)
                self.setFillColor(MUTED)
                self.drawString(MARGIN, 18, footer)
                self.drawRightString(
                    width - MARGIN, 18, page_label.format(page=number, total=total)
                )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=PAGE,
            title=f"{title} – {subtitle}",
            topMargin=HEADER_HEIGHT + 24,
            bottomMargin=48,
            # The frame pads its content by 6pt; offset it so content lines up with MARGIN.
            leftMargin=MARGIN - 6,
            rightMargin=MARGIN - 6,
        )
        doc.build([KeepTogether(elements[:3]), *elements[3:]], canvasmaker=ReportCanvas)

        buffer.seek(0)
        filename = f"audit_report_{inspection_date}.pdf"
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
