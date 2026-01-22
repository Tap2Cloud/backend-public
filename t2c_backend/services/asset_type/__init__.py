from fastapi import File, UploadFile
from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import joinedload

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    AssetType,
    AssetTypeCategory,
    AssetTypeCategoryField,
    AssetTypeField,
    AssetTypeFieldOptions,
    Document,
    Location,
    TypelateImageMapping,
    Typeplate,
    User,
)
from t2c_backend.models.asset_type import AssetTypeDocument as AssetTypeDocumentModel
from t2c_backend.schemas.v1.asset_type import (
    AssetTypeResponse,
    InstructionManualAssetTypeResponse,
)
from t2c_backend.schemas.v1.typeplates import TypeplateImageList
from t2c_backend.utils.enums import DocumentStatus, DocumentType, SortBy
from t2c_backend.utils.errors import NotFoundError


class AssetTypeService:
    _model = AssetType

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.field_repository = BaseRepository(app, session, AssetTypeField)
        self.field_options_repository = BaseRepository(app, session, AssetTypeFieldOptions)
        self.asset_types_documents_repository = BaseRepository(app, session, AssetTypeDocumentModel)
        self.documents_repository = BaseRepository(app, session, Document)

    async def create_asset_type(
        self,
        user_id: int,
        location_id: int,
        asset_type_category_id: int,
        asset_type_data: dict,
        typeplate_images: TypeplateImageList,
        eu_file: UploadFile = File(...),
        instruction_manuals: list[UploadFile] = File(...),
    ):
        asset_type_form = (
            await self.app.services.asset_type_category_service.get_asset_type_category_by_id(
                user_id=user_id,
                asset_type_category_id=asset_type_category_id,
            )
        )
        if not asset_type_form:
            raise NotFoundError(msg="Asset type category not found")

        eu_file_data = None
        if eu_file:
            eu_file_data = await self.documents_repository.save(
                Document(
                    name=eu_file.filename,
                    type=DocumentType.declaration_file,
                    content_type=eu_file.content_type,
                    status=DocumentStatus.pending,
                    user_id=user_id,
                    location_id=location_id,
                )
            )

        typeplate_details = asset_type_data.get("typeplate_details")
        typeplate = None
        if typeplate_details:
            typeplate = Typeplate(
                test_results=typeplate_details.get("test_results") if typeplate_details else None,
                eu_id=typeplate_details.get("eu_id") if typeplate_details else None,
                eu_file=eu_file_data,
                eu_file_id=eu_file_data.id if eu_file_data else None,
                carbon_footprint_label=typeplate_details.get("carbon_footprint_label")
                if typeplate_details
                else None,
            )

        asset_type = AssetType(
            name=asset_type_data.get("name"),
            user_id=user_id,
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

        for typeplate_image in typeplate_images.root if typeplate_images else []:
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

        asset_type_documents = await self.asset_types_documents_repository.save_all(
            [
                AssetTypeDocumentModel(
                    name=doc.filename,
                    content_type=doc.content_type,
                    asset_type_id=asset_type.id,
                    user_id=user_id,
                    location_id=location_id,
                )
                for doc in instruction_manuals or []
            ]
        )

        return {
            "created_asset_type": asset_type,
            "instruction_manuals": asset_type_documents,
            "typeplate": typeplate,
        }

    # TODO add location where condition also fix first with scaler with none
    async def delete_asset_type(self, asset_type_id: int) -> None:
        asset_type = await self.repository.exists(
            id=asset_type_id,
        )

        if asset_type is None:
            raise NotFoundError("Asset type not found")

        await self.repository.delete(id=asset_type_id)

    async def list_asset_types(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        category: str | None,
        organization_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }
        select_query = (
            select(self._model)
            .options(
                joinedload(self._model.documents),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_field_options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.fields).joinedload(AssetTypeField.asset_type_category_field),
            )
            .join(User, User.id == self._model.user_id)
            .join(Location, Location.id == User.location_id)
            .where(Location.organization_id == organization_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=self._model, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        if category:
            category_condition = BaseRepository.parse_filters(AssetTypeCategory, name=category)
            select_query = select_query.filter(
                self._model.asset_type_category.has(*category_condition)
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

    async def list_asset_type_documents(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        is_video: bool,
        is_document: bool,
        organization_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }
        select_query = (
            select(self._model)
            .join(self._model.user)
            .join(User.location)
            .options(
                joinedload(self._model.documents),
            )
            .where(Location.organization_id == organization_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=self._model, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        if is_video:
            select_query = select_query.filter(self._model.video_links.isnot(None))

        if is_document:
            select_query = select_query.join(AssetType.documents).filter(
                AssetTypeDocumentModel.id.isnot(None)
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
        instruction_manuals: list[UploadFile],
    ):
        asset_type = await self.repository.get_one_or_none(
            id=asset_type_id,
            options=[
                joinedload(self._model.documents),
            ],
        )

        if not asset_type:
            raise NotFoundError("Asset type not found")

        new_db_documents = [
            await self.asset_types_documents_repository.save(
                AssetTypeDocumentModel(
                    name=doc.filename,
                    content_type=doc.content_type,
                    asset_type_id=asset_type.id,
                    user_id=user_id,
                    location_id=location_id,
                )
            )
            for doc in instruction_manuals
            if instruction_manuals
        ]

        asset_type.documents.extend(new_db_documents)
        await self.repository.save(asset_type)

        return new_db_documents

    async def delete_asset_type_document(self, asset_type_id: int, document_id: str):
        document = await self.asset_types_documents_repository.exists(
            id=document_id,
            asset_type_id=asset_type_id,
        )

        if not document:
            raise NotFoundError("Asset type document not found")

        return await self.asset_types_documents_repository.delete(id=document_id)


def setup(app, session, *args, **kwargs):
    return app.add_service(AssetTypeService(app, session), session.info["session_id"])
