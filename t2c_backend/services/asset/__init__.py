from datetime import datetime

from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import joinedload

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    Asset,
    AssetType,
    AssetTypeCategory,
    AssetTypeCategoryField,
    AssetTypeField,
    Audit,
    AuditTask,
    Location,
    Organization,
)
from t2c_backend.schemas.v1.asset import (
    AssetResponse,
    CreateAsset,
    DetailedAssetPassResponse,
    UpdateAsset,
)
from t2c_backend.schemas.v1.asset_type_category import DisplayAssetTypeCategory
from t2c_backend.utils.enums import AssetStatus, SortBy
from t2c_backend.utils.errors import NotFoundError


class AssetService:
    _model = Asset

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def create_asset(
        self,
        asset_data: CreateAsset,
        asset_type: AssetType,
        location: Location,
    ):
        location = await self.repository.session.merge(location)
        asset_type = await self.repository.session.merge(asset_type)

        asset = Asset(
            device_id=asset_data.device_id,
            pass_id=self.app.clients.cryptography.encode(f"{location.id}_{asset_data.device_id}"),
            asset_type_id=asset_type.id,
            manufacturing_date=datetime.fromtimestamp(asset_data.manufacturing_date),
            location_id=location.id,
            status=AssetStatus(asset_data.status),
            serial_no=asset_data.serial_no,
            economic_operator=asset_data.economic_operator,
        )
        asset.location = location
        asset.asset_type = asset_type

        return await self.repository.save(asset)

    async def update_asset(
        self,
        asset_id: int,
        updated_asset_data: UpdateAsset,
    ):
        ### TODO: Need to add a lookup for joined models to validate using the organization ID.
        current_db_asset = await self.repository.get_one_or_none(id=asset_id)

        if current_db_asset is None:
            raise NotFoundError("Asset not found")

        update_fields = updated_asset_data.model_dump(exclude_unset=True)

        for key, value in update_fields.items():
            setattr(current_db_asset, key, value)

        updated_asset_data = await self.repository.save(current_db_asset)
        return updated_asset_data

    async def delete_asset(self, asset_id: int, location_id: int) -> None:
        asset = await self.repository.get_one_or_none(id=asset_id, location_id=location_id)

        if not asset:
            raise NotFoundError("Asset not found")

        await self.repository.delete(id=asset_id)

    async def get_asset_by_organization_id(self, asset_id: int, organization_id: int):
        db_asset = await self.repository.get_one_or_none(
            options=[
                joinedload(self._model.location).joinedload(Location.organization),
                joinedload(self._model.asset_type),
                joinedload(self._model.asset_type).options(
                    joinedload(AssetType.documents),
                    joinedload(AssetType.fields).joinedload(
                        AssetTypeField.asset_type_field_options
                    ),
                ),
                joinedload(self._model.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_category_field),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_category_field)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
            ],
            id=asset_id,
            organization_id=organization_id,
        )
        if not db_asset:
            raise NotFoundError("Asset not found")
        return db_asset

    async def list_assets(
        self,
        q: str | None,
        page: int,
        page_size: int,
        location_id: int,
        status: list[AssetStatus] | None,
        categories: list[DisplayAssetTypeCategory] | None,
        sort_by: SortBy | None,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }
        select_query = (
            select(self._model)
            .options(
                joinedload(self._model.asset_type),
                joinedload(self._model.location).joinedload(Location.organization),
                joinedload(self._model.asset_type).options(
                    joinedload(AssetType.documents),
                    joinedload(AssetType.fields).joinedload(
                        AssetTypeField.asset_type_field_options
                    ),
                ),
                joinedload(self._model.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_category_field),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_category_field)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.asset_type).joinedload(AssetType.documents),
            )
            .order_by(sort_order[sort_by])
        )

        if location_id:
            location_filter = BaseRepository.parse_filters(
                model=self._model, location_id=location_id
            )
            select_query = select_query.filter(*location_filter)

        if q:
            serial_no_filter = BaseRepository.parse_filters(self._model, serial_no__ilike=f"%{q}%")
            asset_type_name_filter = BaseRepository.parse_filters(AssetType, name__ilike=f"%{q}%")
            select_query = select_query.filter(
                or_(
                    *serial_no_filter,
                    *[
                        self._model.asset_type.has(condition)
                        for condition in asset_type_name_filter
                    ],
                )
            )

        if status:
            status_condition = BaseRepository.parse_filters(self._model, status__in=status)
            select_query = select_query.filter(*status_condition)

        if categories:
            category_condition = BaseRepository.parse_filters(
                AssetTypeCategory, id__in=[category.id for category in categories]
            )
            select_query = select_query.filter(
                self._model.asset_type.has(AssetType.asset_type_category.has(*category_condition))
            )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_data: [AssetResponse.convert(asset) for asset in asset_data],
        )

    async def list_asset_pass(
        self, q: str | None, page: int, page_size: int, organization_id: int, sort_by: SortBy | None
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }

        select_query = (
            select(self._model)
            .join(self._model.location)
            .where(
                or_(
                    Location.organization_id == organization_id,
                ),
                self._model.device_id.isnot(None),
            )
            .options(
                joinedload(self._model.asset_type),
                joinedload(self._model.asset_type).joinedload(AssetType.fields),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_field_options),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_category_field),
                joinedload(self._model.asset_type).joinedload(AssetType.documents),
                joinedload(self._model.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.user),
                joinedload(self._model.location).joinedload(Location.organization),
                joinedload(self._model.location)
                .joinedload(Location.organization)
                .joinedload(Organization.taxonomy),
                joinedload(self._model.audit),
                joinedload(self._model.audit).joinedload(Audit.audit_tasks),
                joinedload(self._model.audit)
                .joinedload(Audit.audit_tasks)
                .joinedload(AuditTask.documents),
            )
            .order_by(sort_order[sort_by])
        )

        if q:
            serial_no_filter = BaseRepository.parse_filters(self._model, serial_no__ilike=f"%{q}%")
            asset_type_name_filter = BaseRepository.parse_filters(AssetType, name__ilike=f"%{q}%")
            device_id_filter = BaseRepository.parse_filters(self._model, device_id__ilike=f"%{q}%")
            select_query = select_query.filter(
                or_(
                    *serial_no_filter,
                    *device_id_filter,
                    *[
                        self._model.asset_type.has(condition)
                        for condition in asset_type_name_filter
                    ],
                )
            )

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_data: [
                DetailedAssetPassResponse.from_model(asset) for asset in asset_data
            ],
        )

    async def get_asset_pass_by_pass_id(self, pass_id: int, gtin: str | None):
        asset = await self.repository.get_one_or_none(
            pass_id=pass_id,
            options=[
                joinedload(self._model.location),
                joinedload(self._model.location).joinedload(Location.organization),
                joinedload(self._model.location)
                .joinedload(Location.organization)
                .joinedload(Organization.taxonomy),
                joinedload(self._model.asset_type),
                joinedload(self._model.asset_type).joinedload(AssetType.fields),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.fields)
                .joinedload(AssetTypeField.asset_type_field_options),
                joinedload(self._model.asset_type).joinedload(AssetType.documents),
                joinedload(self._model.asset_type).joinedload(AssetType.asset_type_category),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.fields)
                .joinedload(AssetTypeCategoryField.asset_type_category_group),
                joinedload(self._model.asset_type)
                .joinedload(AssetType.asset_type_category)
                .joinedload(AssetTypeCategory.user),
                joinedload(self._model.audit),
                joinedload(self._model.audit).joinedload(Audit.audit_tasks),
                joinedload(self._model.audit)
                .joinedload(Audit.audit_tasks)
                .joinedload(AuditTask.documents),
            ],
        )

        if not asset:
            raise NotFoundError(msg="No asset found")

        if gtin and asset.asset_type.gtin != gtin:
            raise NotFoundError(f"No asset found for {gtin} gtin")

        return asset

    async def get_asset_by_id(self, asset_id: int, organization_id: int):
        select_query = (
            select(self._model)
            .join(self._model.location)
            .where(
                or_(
                    Location.organization_id == organization_id,
                ),
                self._model.id == asset_id,
            )
            .options(
                joinedload(self._model.location),
                joinedload(self._model.asset_type),
                joinedload(self._model.audit),
                joinedload(self._model.audit).joinedload(Audit.audit_tasks),
                joinedload(self._model.audit)
                .joinedload(Audit.audit_tasks)
                .joinedload(AuditTask.documents),
            )
        )

        query = await self.repository.execute(select_query)
        asset = query.unique().scalar_one_or_none()
        if asset is None:
            raise NotFoundError(msg="Asset not found")
        return asset


def setup(app, session, *args, **kwargs):
    return app.add_service(AssetService(app, session), session.info["session_id"])
