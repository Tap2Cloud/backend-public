import uuid
from datetime import date, datetime, time

from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import joinedload, selectinload
from starlette.datastructures import UploadFile as StarletteUploadFile

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    AssetType,
    AssetTypeCategory,
    Location,
    TypelateImageMapping,
    Typeplate,
    TypeplateDocument,
    TypeplateImage,
    User,
)
from t2c_backend.schemas.v1.typeplates import (
    AssetTypeTypeplateResponse,
    TypeplateImageList,
    TypeplateRequest,
)
from t2c_backend.utils.enums import DocumentFor, SortBy
from t2c_backend.utils.errors import NotFoundError


class TypeplateService:
    _model = Typeplate

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.typeplate_image_repository = BaseRepository(app, session, TypeplateImage)
        self.selected_image_repository = BaseRepository(app, session, TypelateImageMapping)
        self.typeplate_document_repository = BaseRepository(app, session, TypeplateDocument)

    async def get_typeplate_images(self):
        return await self.typeplate_image_repository.list(
            orders=asc("id"),
        )

    async def list_typeplates(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        typeplate_created_start_date: date,
        typeplate_created_end_date: date,
        organization_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }

        select_query = (
            select(AssetType)
            .join(AssetType.typeplate)
            .outerjoin(AssetType.asset_type_category)
            .options(
                joinedload(AssetType.typeplate).joinedload(Typeplate.documents),
                joinedload(AssetType.typeplate).joinedload(Typeplate.typeplate_images),
                joinedload(AssetType.typeplate)
                .joinedload(Typeplate.typeplate_images)
                .joinedload(TypelateImageMapping.typeplate_image),
                joinedload(AssetType.asset_type_category),
            )
            .join(User, User.id == AssetType.user_id)
            .join(Location, Location.id == User.location_id)
            .where(Location.organization_id == organization_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            asset_type_category_filter = BaseRepository.parse_filters(
                AssetTypeCategory, name__ilike=f"%{q}%"
            )
            asset_type_filters = BaseRepository.parse_filters(model=AssetType, name__ilike=f"%{q}%")
            select_query = select_query.filter(
                or_(
                    *asset_type_category_filter,
                    *asset_type_filters,
                )
            )

        if typeplate_created_start_date and typeplate_created_end_date:
            typeplate_created_start_date = datetime.combine(typeplate_created_start_date, time.min)
            typeplate_created_end_date = datetime.combine(typeplate_created_end_date, time.max)
            filters = BaseRepository.parse_filters(
                model=Typeplate,
                created_at__between=[typeplate_created_start_date, typeplate_created_end_date],
            )
            select_query = select_query.filter(*filters)

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_type_data: [
                AssetTypeTypeplateResponse.convert(
                    asset_type=asset_type,
                    eu_file_data=asset_type.typeplate.documents,
                    typeplate_documents=[
                        img.typeplate_image for img in asset_type.typeplate.typeplate_images
                    ],
                )
                for asset_type in asset_type_data
            ],
        )

    async def get_typeplate_details_by_id(self, typeplate_id: int):
        typeplate = await self.repository.get_one_or_none(
            id=typeplate_id,
            options=[
                joinedload(self._model.documents),
                joinedload(self._model.typeplate_images),
                joinedload(self._model.typeplate_images).joinedload(
                    TypelateImageMapping.typeplate_image
                ),
            ],
        )

        if not typeplate:
            raise NotFoundError(msg="Typeplate not found")

        return typeplate

    async def update_typeplate(
        self,
        typeplate_id: int,
        typeplate_data: TypeplateRequest,
        user_id: int,
        location_id: int,
        organization_id: int,
        typeplate_images: TypeplateImageList | None,
        eu_file: UploadFile | None = File(...),
    ):
        typeplate = await self.repository.get_one_or_none(
            id=typeplate_id,
            options=[
                joinedload(self._model.asset_type),
                joinedload(self._model.asset_type).joinedload(AssetType.user),
                selectinload(self._model.documents),
                selectinload(self._model.typeplate_images),
            ],
        )
        if not typeplate or typeplate.asset_type.user.location_id != location_id:
            raise NotFoundError(msg="Typeplate not found")

        for key, value in typeplate_data.model_dump(exclude={"typeplate_images"}).items():
            setattr(typeplate, key, value)

        if typeplate.documents:
            await self.app.clients.storage.delete_document(
                organization_id=organization_id,
                document_for=DocumentFor.EuFiles,
                file_id=typeplate.documents[0].id,
                filename=typeplate.documents[0].name,
            )
            typeplate.documents.clear()
        if isinstance(eu_file, StarletteUploadFile):
            eu_file_data = await self.typeplate_document_repository.save(
                TypeplateDocument(
                    name=eu_file.filename,
                    content_type=eu_file.content_type,
                    typeplate_id=typeplate.id,
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
            typeplate.documents.append(eu_file_data)

        typeplate.typeplate_images.clear()
        for typeplate_image in typeplate_images or []:
            image = await self.app.services.typeplate_service.typeplate_image_repository.get(
                typeplate_image.id
            )
            if not image:
                raise NotFoundError(msg="Typeplate image not found")

            typeplate.typeplate_images.append(
                TypelateImageMapping(
                    typeplate_id=typeplate.id,
                    typeplate_image_id=image.id,
                )
            )

        return await self.repository.save(typeplate)

    async def delete_typeplate_document(
        self,
        typeplate_id: int,
        document_id: str,
        location_id: int,
        organization_id: int,
    ):
        typeplate_document = await self.typeplate_document_repository.get_one_or_none(
            typeplate_id=typeplate_id,
            document_id=document_id,
            location_id=location_id,
        )

        if not typeplate_document:
            raise NotFoundError(msg="Typeplate document not found")

        await self.app.clients.storage.delete_document(
            organization_id=organization_id,
            document_for=DocumentFor.EuFiles,
            file_id=typeplate_document.id,
            filename=typeplate_document.name,
        )

        await self.typeplate_document_repository.delete(id=typeplate_document.id)

    async def get_typeplate_document(
        self, eu_file_id: uuid.UUID, typeplate_id: int, organization_id: int
    ):
        typeplate_document = await self.typeplate_document_repository.get_one_or_none(
            id=eu_file_id,
            typeplate_id=typeplate_id,
            options=[joinedload(TypeplateDocument.location)],
        )
        if not typeplate_document or typeplate_document.location.organization_id != organization_id:
            raise NotFoundError("typeplate document not found")

        return StreamingResponse(
            self.app.clients.storage.get_document(
                organization_id=organization_id,
                document_for=DocumentFor.EuFiles,
                file_id=typeplate_document.id,
                file_name=typeplate_document.name,
            ),
            media_type=str(typeplate_document.content_type),
            headers={"Content-Disposition": f'attachment; filename="{typeplate_document.name}"'},
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(TypeplateService(app, session), session.info["session_id"])
