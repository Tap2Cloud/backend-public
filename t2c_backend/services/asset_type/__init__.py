import copy
import mimetypes
import uuid

from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from starlette.datastructures import UploadFile as StarletteUploadFile

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    AssetType,
    AssetTypeCategory,
    AssetTypeCategoryField,
    AssetTypeField,
    AssetTypeFieldOptions,
    TypelateImageMapping,
    Typeplate,
    TypeplateDocument,
)
from t2c_backend.models.asset_type import AssetTypeDocument as AssetTypeDocumentModel
from t2c_backend.schemas.v1.asset_type import (
    AssetTypeResponse,
    InstructionManualAssetTypeResponse,
    UpdateAssetTypeRequest,
)
from t2c_backend.schemas.v1.asset_type_category import DisplayAssetTypeCategory
from t2c_backend.schemas.v1.typeplates import TypeplateImageRequest
from t2c_backend.utils.enums import DocumentFor, InputType, SortBy
from t2c_backend.utils.errors import NotFoundError


class AssetTypeService:
    _model = AssetType

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.category_fields_repository = BaseRepository(app, session, AssetTypeCategoryField)
        self.field_repository = BaseRepository(app, session, AssetTypeField)
        self.field_options_repository = BaseRepository(app, session, AssetTypeFieldOptions)
        self.asset_types_documents_repository = BaseRepository(app, session, AssetTypeDocumentModel)
        self.typeplate_documents_repository = BaseRepository(app, session, TypeplateDocument)

    async def create_asset_type(
        self,
        user_id: int,
        location_id: int,
        organization_id: int,
        asset_type_category_id: int,
        asset_type_data: dict,
        typeplate_images: list[TypeplateImageRequest],
        eu_file: UploadFile = File(...),
        instruction_manuals: list[UploadFile] = File(...),
        custom_media_fields: list[UploadFile] = File(None),
    ):
        asset_type_form = (
            await self.app.services.asset_type_category_service.get_asset_type_category_by_id(
                location_id=location_id,
                asset_type_category_id=asset_type_category_id,
            )
        )
        if not asset_type_form:
            raise NotFoundError(msg="Asset type category not found")

        typeplate_details = asset_type_data.get("typeplate_details")
        typeplate = None
        if typeplate_details and asset_type_form.has_typeplates:
            typeplate = Typeplate(
                test_results=typeplate_details.get("test_results") if typeplate_details else None,
                eu_id=typeplate_details.get("eu_id") if typeplate_details else None,
                carbon_footprint_label=typeplate_details.get("carbon_footprint_label")
                if typeplate_details
                else None,
            )

        asset_type = AssetType(
            name=asset_type_data.get("name"),
            user_id=user_id,
            location_id=location_id,
            video_links=asset_type_data.get("video_links"),
            video_title=asset_type_data.get("video_title"),
            web_link=asset_type_data.get("web_link"),
            web_link_title=asset_type_data.get("web_link_title"),
            description=asset_type_data.get("description"),
            weight=asset_type_data.get("weight"),
            manufacturer=asset_type_data.get("manufacturer"),
            asset_type_category_id=asset_type_form.id,
            typeplate=typeplate,
        )

        for at in asset_type_data.get("fields", []):
            asset_type_field = AssetTypeField(
                field_id=at["field_id"],
                response_value=at["response_value"],
                asset_type_id=asset_type.id,
                asset_type_field_options=[
                    AssetTypeFieldOptions(
                        option_id=opt["option_id"],
                        asset_type_field_id=at["field_id"],
                    )
                    for opt in at.get("asset_type_field_options", [])
                ],
            )
            asset_type.fields.append(asset_type_field)

        asset_type = await self.repository.save(asset_type)

        for at in asset_type.fields:
            asset_type_category_field = await self.category_fields_repository.get_one_or_none(
                id=at.field_id
            )
            if (
                asset_type_category_field.field_type in [InputType.image, InputType.file]
                and custom_media_fields
            ):
                file = next(
                    (f for f in custom_media_fields if f.filename == at.response_value), None
                )
                if file:
                    await self.app.clients.storage.save_document(
                        organization_id=organization_id,
                        document_for=DocumentFor.AssetTypeFieldSpecificDocuments,
                        file_id=at.id,
                        file=file,
                    )

        for typeplate_image in typeplate_images if typeplate_images else []:
            image = await self.app.services.typeplate_service.typeplate_image_repository.get(
                typeplate_image.id
            )

            if not image:
                raise NotFoundError(msg="Typeplate image not found")

            await self.app.services.typeplate_service.selected_image_repository.save(
                TypelateImageMapping(
                    typeplate_id=asset_type.typeplate.id,
                    typeplate_image_id=image.id,
                )
            )
        if isinstance(eu_file, StarletteUploadFile):
            eu_file_data = await self.typeplate_documents_repository.save(
                TypeplateDocument(
                    name=eu_file.filename,
                    content_type=eu_file.content_type,
                    typeplate_id=asset_type.typeplate.id,
                    user_id=user_id,
                    location_id=location_id,
                )
            )
            await self.app.clients.storage.save_document(
                organization_id=organization_id,
                document_for=DocumentFor.EuFiles,
                file_id=eu_file_data.id,
                file=eu_file,
            )

        asset_type_documents = None
        for doc in instruction_manuals or []:
            asset_type_documents = await self.asset_types_documents_repository.save(
                AssetTypeDocumentModel(
                    name=doc.filename,
                    content_type=doc.content_type,
                    asset_type_id=asset_type.id,
                    user_id=user_id,
                    location_id=location_id,
                )
            )
            await self.app.clients.storage.save_document(
                organization_id=organization_id,
                document_for=DocumentFor.InstructionManualDocuments,
                file_id=asset_type_documents.id,
                file=doc,
            )

        return {
            "created_asset_type": asset_type,
            "instruction_manuals": asset_type_documents,
            "typeplate": typeplate,
        }

    async def update_asset_type(
        self,
        asset_type_id: int,
        asset_type_details: UpdateAssetTypeRequest,
        location_id: int,
    ):
        db_asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                joinedload(self._model.typeplate),
                joinedload(self._model.asset_type_category),
            ],
        )
        if not db_asset_type:
            raise NotFoundError("Asset type not found")

        db_asset_type.name = asset_type_details.name
        db_asset_type.video_links = asset_type_details.video_links
        db_asset_type.video_title = asset_type_details.video_title
        db_asset_type.web_link = asset_type_details.web_link
        db_asset_type.web_link_title = asset_type_details.web_link_title
        db_asset_type.description = asset_type_details.description
        db_asset_type.weight = asset_type_details.weight
        db_asset_type.manufacturer = asset_type_details.manufacturer

        excluded_types = [InputType.image, InputType.file]
        db_asset_type.fields = [
            f
            for f in db_asset_type.fields
            if f.asset_type_category_field.field_type in excluded_types
        ]

        excluded_field_ids = copy.deepcopy(db_asset_type.fields)
        excluded_field_ids = [f.field_id for f in excluded_field_ids]

        for at in asset_type_details.fields:
            if at.field_id in excluded_field_ids:
                continue
            asset_type_field = AssetTypeField(
                field_id=at.field_id,
                response_value=at.response_value,
                asset_type_id=db_asset_type.id,
                asset_type_field_options=[
                    AssetTypeFieldOptions(
                        option_id=opt.option_id,
                        asset_type_field_id=at.field_id,
                    )
                    for opt in at.asset_type_field_options
                ],
            )
            db_asset_type.fields.append(asset_type_field)

        await self.repository.save(db_asset_type)

    async def delete_asset_type(self, asset_type_id: int, location_id: int) -> None:
        asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                joinedload(self._model.location),
                joinedload(self._model.typeplate),
                joinedload(self._model.typeplate).joinedload(Typeplate.documents),
                joinedload(self._model.documents),
                joinedload(self._model.fields),
            ],
        )

        if asset_type is None:
            raise NotFoundError("Asset type not found")

        organization_id = asset_type.location.organization_id

        if asset_type.documents:
            for instruction_manual in asset_type.documents:
                await self.app.clients.storage.delete_document(
                    organization_id=organization_id,
                    document_for=DocumentFor.InstructionManualDocuments,
                    file_id=instruction_manual.id,
                    filename=instruction_manual.name,
                )
        if asset_type.typeplate:
            for typeplate_document in asset_type.typeplate.documents:
                await self.app.clients.storage.delete_document(
                    organization_id=organization_id,
                    document_for=DocumentFor.EuFiles,
                    file_id=typeplate_document.id,
                    filename=typeplate_document.name,
                )

        for asset_type_field in asset_type.fields:
            await self.app.clients.storage.delete_document(
                organization_id=organization_id,
                document_for=DocumentFor.AssetTypeFieldSpecificDocuments,
                file_id=asset_type_field.id,
                filename=asset_type_field.response_value,
            )

        await self.repository.delete(id=asset_type_id)

    async def list_asset_types(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        categories: list[DisplayAssetTypeCategory] | None,
        location_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.id),
            SortBy.Oldest: asc(self._model.id),
        }
        select_query = (
            select(self._model)
            .options(
                selectinload(self._model.documents),
                selectinload(self._model.fields).options(
                    selectinload(AssetTypeField.asset_type_field_options),
                    joinedload(AssetTypeField.asset_type_category_field),
                ),
                joinedload(self._model.asset_type_category).options(
                    selectinload(AssetTypeCategory.fields).options(
                        selectinload(AssetTypeCategoryField.options),
                        joinedload(AssetTypeCategoryField.asset_type_category_group),
                    ),
                ),
                joinedload(self._model.typeplate).options(
                    selectinload(Typeplate.documents),
                    selectinload(Typeplate.typeplate_images),
                ),
            )
            .where(self._model.location_id == location_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=self._model, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        if categories:
            select_query = select_query.filter(
                self._model.asset_type_category_id.in_(
                    [int(category.id) for category in categories]
                )
            )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_type_data: [
                AssetTypeResponse.convert(
                    asset_type=asset_type,
                    instruction_manuals_data=[document for document in asset_type.documents],
                )
                for asset_type in asset_type_data
                if asset_type.fields
            ],
        )

    async def get_asset_type_by_id(self, asset_type_id: int, location_id: int):
        asset_type_details = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                selectinload(self._model.documents),
                selectinload(self._model.fields).options(
                    selectinload(AssetTypeField.asset_type_field_options),
                    joinedload(AssetTypeField.asset_type_category_field),
                ),
                joinedload(self._model.asset_type_category).options(
                    selectinload(AssetTypeCategory.fields).options(
                        selectinload(AssetTypeCategoryField.options),
                        joinedload(AssetTypeCategoryField.asset_type_category_group),
                    ),
                ),
                joinedload(self._model.typeplate).options(
                    selectinload(Typeplate.documents),
                    selectinload(Typeplate.typeplate_images),
                ),
                joinedload(self._model.user),
            ],
        )
        if not asset_type_details:
            raise NotFoundError("Asset type not found")
        return asset_type_details

    async def list_asset_type_documents(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        is_video: bool,
        is_document: bool,
        location_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }
        select_query = (
            select(self._model)
            .options(
                joinedload(self._model.documents),
            )
            .where(self._model.location_id == location_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=self._model, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        if is_video:
            select_query = select_query.filter(self._model.video_links.isnot(None))

        if is_document:
            select_query = select_query.filter(
                exists().where(AssetTypeDocumentModel.asset_type_id == self._model.id)
            )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            transformer=lambda asset_type_data: [
                InstructionManualAssetTypeResponse.convert(asset_type, asset_type.documents)
                for asset_type in asset_type_data
            ],
        )

    async def save_asset_type_document(
        self,
        asset_type_id: int,
        user_id: int,
        location_id: int,
        organization_id: int,
        documents: list[UploadFile],
    ):
        asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                joinedload(self._model.documents),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_field_options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_category_field),
                joinedload(self._model.typeplate),
                joinedload(self._model.typeplate).joinedload(Typeplate.documents),
                joinedload(self._model.typeplate).joinedload(Typeplate.typeplate_images),
                joinedload(self._model.user),
            ],
        )

        if not asset_type:
            raise NotFoundError("Asset type not found")

        new_db_documents = []
        for doc in documents or []:
            new_document = await self.asset_types_documents_repository.save(
                AssetTypeDocumentModel(
                    name=doc.filename,
                    content_type=doc.content_type,
                    asset_type_id=asset_type.id,
                    user_id=user_id,
                    location_id=location_id,
                )
            )
            await self.app.clients.storage.save_document(
                organization_id=organization_id,
                document_for=DocumentFor.InstructionManualDocuments,
                file_id=new_document.id,
                file=doc,
            )
            new_db_documents.append(new_document)

        asset_type.documents.extend(new_db_documents)

        return await self.repository.save(asset_type)

    async def save_asset_type_custom_field_document(
        self,
        asset_type_id: int,
        custom_field_id: int,
        location_id: int,
        organization_id: int,
        documents: UploadFile,
    ):
        asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                joinedload(self._model.documents),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_field_options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_category_field),
                joinedload(self._model.typeplate),
                joinedload(self._model.typeplate).joinedload(Typeplate.documents),
                joinedload(self._model.typeplate).joinedload(Typeplate.typeplate_images),
                joinedload(self._model.user),
            ],
        )

        if not asset_type:
            raise NotFoundError("Asset type not found")

        for asset_type_field in asset_type.fields:
            if custom_field_id != asset_type_field.field_id:
                continue
            await self.app.clients.storage.delete_document(
                organization_id=organization_id,
                document_for=DocumentFor.AssetTypeFieldSpecificDocuments,
                file_id=asset_type_field.id,
                filename=asset_type_field.response_value,
            )
            custom_field_value_id = asset_type_field.id
            asset_type_field.response_value = documents.filename
            break
        else:
            asset_type_field = AssetTypeField(
                field_id=custom_field_id,
                response_value=documents.filename,
                asset_type_id=asset_type.id,
                asset_type_field_options=[],
            )
            try:
                custom_field_value_id = await self.field_repository.save(asset_type_field)
            except IntegrityError:
                raise NotFoundError("Custom Field not found")
            custom_field_value_id = custom_field_value_id.id

        await self.app.clients.storage.save_document(
            organization_id=organization_id,
            document_for=DocumentFor.AssetTypeFieldSpecificDocuments,
            file_id=custom_field_value_id,
            file=documents,
        )

        return await self.repository.save(asset_type)

    async def delete_asset_type_document(
        self, asset_type_id: int, document_id: uuid.UUID, location_id: int
    ):
        document = await self.asset_types_documents_repository.get_one_or_none(
            id=document_id,
            asset_type_id=asset_type_id,
            location_id=location_id,
            options=[joinedload(AssetTypeDocumentModel.location)],
        )

        if not document:
            raise NotFoundError("Asset type document not found")

        await self.app.clients.storage.delete_document(
            organization_id=document.location.organization_id,
            document_for=DocumentFor.InstructionManualDocuments,
            file_id=document.id,
            filename=document.name,
        )

        return await self.asset_types_documents_repository.delete(id=document_id)

    async def delete_asset_type_custom_field_document(
        self, asset_type_id: int, document_id: int, location_id: int
    ):
        document = await self.field_repository.get_one_or_none(
            id=document_id,
            asset_type_id=asset_type_id,
            join=[AssetTypeField.asset_type],
            where=[AssetType.location_id == location_id],
            options=[
                joinedload(AssetTypeField.asset_type),
                joinedload(AssetTypeField.asset_type).joinedload(AssetType.location),
            ],
        )

        if not document:
            raise NotFoundError("Asset type field's document not found")

        await self.app.clients.storage.delete_document(
            organization_id=document.asset_type.location.organization_id,
            document_for=DocumentFor.AssetTypeFieldSpecificDocuments,
            file_id=document.id,
            filename=document.response_value,
        )
        document.response_value = ""
        return await self.field_repository.save(document)

    async def get_asset_type_document(
        self,
        asset_type_id: int,
        location_id: int,
        document_type: DocumentFor,
        document_id: str,
        document_name: str,
    ):
        asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            location_id=location_id,
            options=[
                joinedload(self._model.location),
            ],
        )

        if not asset_type:
            raise NotFoundError("Asset type not found")

        mime_type, encoding = mimetypes.guess_type(document_name)

        return StreamingResponse(
            self.app.clients.storage.get_document(
                organization_id=asset_type.location.organization_id,
                document_for=document_type,
                file_id=document_id,
                file_name=document_name,
            ),
            media_type=str(mime_type),
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(AssetTypeService(app, session), session.info["session_id"])
