import datetime

from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import joinedload

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    AssetType,
    Location,
    TypelateImageMapping,
    Typeplate,
    TypeplateDocument,
    TypeplateImage,
    User,
)
from t2c_backend.schemas.v1.typeplates import AssetTypeTypeplateResponse
from t2c_backend.utils.enums import SortBy


class TypeplateService:
    _model = Typeplate

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.typeplate_image_repository = BaseRepository(app, session, TypeplateImage)
        self.selected_image_repository = BaseRepository(app, session, TypelateImageMapping)

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
        typeplate_created_start_date: datetime.date,
        typeplate_created_end_date: datetime.date,
        organization_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }

        select_query = (
            select(AssetType)
            .join(AssetType.typeplate)
            .join(AssetType.user)
            .join(User.location)
            .options(
                joinedload(AssetType.typeplate)
                .joinedload(Typeplate.typeplate_documents)
                .joinedload(TypeplateDocument.document),
                joinedload(AssetType.typeplate).joinedload(Typeplate.eu_file),
                joinedload(AssetType.typeplate).joinedload(Typeplate.typeplate_images),
                joinedload(AssetType.typeplate)
                .joinedload(Typeplate.typeplate_images)
                .joinedload(TypelateImageMapping.typeplate_image),
            )
            .where(Location.organization_id == organization_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=AssetType, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        if typeplate_created_start_date and typeplate_created_end_date:
            filters = BaseRepository.parse_filters(
                model=Typeplate,
                created_at__between=[typeplate_created_start_date, typeplate_created_end_date],
            )
            select_query = select_query.filter(*filters)

        return await apaginate(
            self.app.services.asset_type_service.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_type_data: [
                AssetTypeTypeplateResponse.convert(
                    asset_type=asset_type,
                    eu_file_data=asset_type.typeplate.eu_file,
                    typeplate_documents=[
                        img.typeplate_image for img in asset_type.typeplate.typeplate_images
                    ],
                )
                for asset_type in asset_type_data
            ],
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(TypeplateService(app, session), session.info["session_id"])
