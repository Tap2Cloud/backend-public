from datetime import datetime, time

from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import contains_eager, joinedload

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Asset, AssetType, Location
from t2c_backend.models.service import Service
from t2c_backend.schemas.v1.service import AssetServiceResponse, CreateService
from t2c_backend.utils.enums import ServiceTypes, SortBy
from t2c_backend.utils.errors import BadRequestError, NotFoundError
from t2c_backend.utils.misc import aware_utcnow


class ServiceService:
    _model = Service

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.asset_repository = BaseRepository(app, session, Asset)

    async def create_service(self, service_data: CreateService, asset_id: int, location_id: int):
        asset = await self.app.services.asset_service.repository.get_one_or_none(
            options=[
                joinedload(Asset.asset_type).joinedload(AssetType.asset_type_category),
            ],
            id=asset_id,
            location_id=location_id,
        )

        if not asset:
            raise NotFoundError(msg="Asset not found")

        service = Service(
            service_name=service_data.service_name,
            service_provider_name=service_data.service_provider_name,
            contact=service_data.contact,
            expire_date=datetime.fromtimestamp(service_data.expire_date),
            service_date=datetime.fromtimestamp(service_data.service_date),
            service_type=ServiceTypes(service_data.service_type),
            web=service_data.web,
            email=service_data.email,
            asset_id=asset.id,
        )
        service.asset = asset

        return await self.repository.save(service)

    async def update_service(self, service_data: CreateService, service_id: int, location_id: int):
        stmt = (
            select(Service)
            .join(Service.asset)
            .filter(Service.id == service_id, Asset.location_id == location_id)
        )

        result = await self.repository.execute(stmt)
        service = result.scalar_one_or_none()

        if not service:
            raise NotFoundError(msg="Service not found")

        if service.expire_date <= aware_utcnow():
            raise BadRequestError("Expired service details can not update")

        update_fields = service_data.model_dump()
        update_fields["expire_date"] = datetime.fromtimestamp(service_data.expire_date)

        for key, value in update_fields.items():
            setattr(service, key, value)

        return await self.repository.save(service)

    async def delete_service(self, service_id: int, location_id: int) -> None:
        service = await self.repository.get_one_or_none(
            id=service_id,
            join=[self._model.asset],
            where=[Asset.location_id == location_id],
        )

        if not service:
            raise NotFoundError("Service not found")

        await self.repository.delete(id=service_id)

    async def list_services(
        self,
        location_id: int,
        q: str,
        sort_by: SortBy | None,
        service_start_date: datetime.date,
        service_end_date: datetime.date,
        expire_start_date: datetime.date,
        expire_end_date: datetime.date,
        page: int,
        page_size: int,
    ):
        _model = Asset
        sort_order = {
            SortBy.Latest: desc(_model.created_at),
            SortBy.Oldest: asc(_model.created_at),
        }

        asset_filters = []
        service_filters = []

        if service_start_date and service_end_date:
            service_start_date = datetime.combine(service_start_date, time.min)
            service_end_date = datetime.combine(service_end_date, time.max)
            filters = Service.service_date.between(service_start_date, service_end_date)
            service_filters.append(filters)
            asset_filters.append(Asset.services.any(filters))

        if expire_start_date and expire_end_date:
            expire_start_date = datetime.combine(expire_start_date, time.min)
            expire_end_date = datetime.combine(expire_end_date, time.max)
            filters = Service.expire_date.between(expire_start_date, expire_end_date)
            service_filters.append(filters)
            asset_filters.append(Asset.services.any(filters))

        if q:
            serial_no_filter = BaseRepository.parse_filters(_model, serial_no__ilike=f"%{q}%")
            asset_type_name_filter = BaseRepository.parse_filters(AssetType, name__ilike=f"%{q}%")
            asset_filters.append(
                or_(
                    *serial_no_filter,
                    *[Asset.asset_type.has(condition) for condition in asset_type_name_filter],
                )
            )

        select_query = (
            select(_model)
            .options(
                joinedload(Asset.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(
                    Asset.services.and_(*service_filters) if service_filters else Asset.services
                ),
            )
            .order_by(sort_order[sort_by])
            .filter(*asset_filters)
            .filter(_model.location_id == location_id)
        )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda assets: [AssetServiceResponse.convert(asset) for asset in assets],
        )

    async def get_service_by_id(self, service_id: int, organization_id: int):
        select_query = (
            select(Asset)
            .options(
                joinedload(Asset.asset_type),
                contains_eager(Asset.services),
            )
            .join(Location, Location.id == Asset.location_id)
            .join(Service, Service.asset_id == Asset.id)
            .where((Location.organization_id == organization_id) & (Service.id == service_id))
        )

        result = await self.repository.execute(select_query)
        assets = result.unique().scalar_one_or_none()
        if not assets:
            raise NotFoundError("service not found")
        return assets


def setup(app, session, *args, **kwargs):
    return app.add_service(ServiceService(app, session), session.info["session_id"])
