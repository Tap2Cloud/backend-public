from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from t2c_backend.core.pagination import CustomPage, CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    AssetTypeCategory,
    AssetTypeCategoryField,
    AssetTypeCategoryFieldOption,
    AssetTypeCategoryGroup,
    Location,
    Organization,
    User,
)
from t2c_backend.schemas.v1.asset_type_category import (
    AssetTypeCategoryResponse,
    UpdateAssetTypeCategoryRequest,
)
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.errors import AlreadyExistsError, BadRequestError, NotFoundError


class AssetTypeCategoryService:
    _model = AssetTypeCategory

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.fields_repository = BaseRepository(app, session, AssetTypeCategoryField)
        self.field_options_repository = BaseRepository(app, session, AssetTypeCategoryFieldOption)
        self.asset_type_category_groups_repository = BaseRepository(
            app, session, AssetTypeCategoryGroup
        )

    async def create_asset_type_category(self, user_id: int, form_data: dict):
        form = AssetTypeCategory(
            user_id=user_id,
            name=form_data.get("name"),
            has_typeplates=form_data.get("has_typeplates"),
        )
        form.user = await self.app.services.user_service.repository.get(user_id)
        for ff in form_data.get("fields", []):
            asset_type_category_group = await self.asset_type_category_groups_repository.get(
                ff["field_group_id"]
            )
            if not asset_type_category_group:
                raise NotFoundError("Asset type category group not found")
            form_field_options = []
            form_field = AssetTypeCategoryField(
                field_name=ff.get("field_name"),
                field_place_holder=ff.get("field_place_holder"),
                field_display_name=ff.get("field_display_name"),
                field_is_required=ff.get("field_is_required"),
                field_order=ff.get("field_order"),
                field_type=ff.get("field_type"),
                asset_type_category_id=form.id,
                asset_type_category_group_id=asset_type_category_group.id,
                asset_type_category_group=asset_type_category_group,
            )
            for ffo in ff.get("options", []):
                form_field_options.append(
                    AssetTypeCategoryFieldOption(
                        option_label=ffo.get("option_label"),
                        option_id=ffo.get("option_id"),
                        asset_field_type_category_field_id=form_field.id,
                    ),
                )
            form_field.options = form_field_options
            form.fields.append(form_field)
        try:
            return await self.repository.save(form)
        except IntegrityError:
            raise AlreadyExistsError("Category name already exist")

    async def update_asset_type_category(
        self,
        asset_type_category_id: int,
        updated_asset_type_category_data: UpdateAssetTypeCategoryRequest,
        organization_id: int,
    ):
        db_asset_type_details = await self.repository.get_one_or_none(
            id=asset_type_category_id,
            options=[
                joinedload(self._model.user),
                joinedload(self._model.user).joinedload(User.location),
            ],
        )
        if (
            not db_asset_type_details
            or db_asset_type_details.user.location.organization_id != organization_id
        ):
            raise NotFoundError("Asset type category not found")

        for key, value in updated_asset_type_category_data.model_dump(
            exclude={"fields"}, exclude_none=True
        ).items():
            setattr(db_asset_type_details, key, value)

        for category_field in updated_asset_type_category_data.fields:
            asset_type_category_field = next(
                (f for f in db_asset_type_details.fields if f.id == category_field.id), None
            )
            if not asset_type_category_field:
                raise NotFoundError("Asset type category field not found")
            if not await self.asset_type_category_groups_repository.get_one_or_none(
                id=category_field.asset_type_category_group_id
            ):
                raise NotFoundError("Asset type category group not found")

            for key, value in category_field.model_dump(
                exclude={"id", "options"}, exclude_none=True
            ).items():
                if key == "field_order":
                    setattr(asset_type_category_field, key, -value)
                else:
                    setattr(asset_type_category_field, key, value)

            for option in category_field.options:
                asset_type_category_field_option = next(
                    (o for o in asset_type_category_field.options if o.id == option.id), None
                )
                if not asset_type_category_field_option:
                    raise NotFoundError("Asset type category field options not found")
                for key, value in option.model_dump(exclude={"id"}, exclude_none=True).items():
                    setattr(asset_type_category_field_option, key, value)

            await self.fields_repository.save(asset_type_category_field)

        all_field_orders = []
        for field in db_asset_type_details.fields:
            if field.field_order in all_field_orders:
                raise BadRequestError("Duplicate field order found")
            all_field_orders.append(field.field_order)
            field.field_order = abs(field.field_order)

        return await self.repository.save(db_asset_type_details)

    async def get_asset_type_category_by_id(self, asset_type_category_id: int, user_id: int):
        return await self.repository.get_one_or_none(user_id=user_id, id=asset_type_category_id)

    async def delete_asset_type_category(self, asset_type_category_id: int):
        return await self.repository.delete(id=asset_type_category_id)

    async def list_asset_type_category(self, organization_id: int):
        stmt = (
            select(AssetTypeCategory)
            .join(User, User.id == AssetTypeCategory.user_id)
            .join(Location, Location.id == User.location_id)
            .where(Location.organization_id == organization_id)
            .where(AssetTypeCategory.asset_type.any())
            .options(joinedload(AssetTypeCategory.asset_type))
            .order_by(desc(AssetTypeCategory.id))
        )

        result = await self.repository.execute(stmt)
        return result.scalars().unique().all()

    async def list_asset_type_categories(
        self,
        q: str | None,
        sort_by: SortBy | None,
        page: int,
        page_size: int,
        organization_id: int,
    ):
        sort_order = {
            SortBy.Latest: desc(self._model.created_at),
            SortBy.Oldest: asc(self._model.created_at),
        }
        select_query = (
            select(self._model)
            .options(
                joinedload(self._model.user),
                joinedload(self._model.fields).joinedload(
                    AssetTypeCategoryField.asset_type_category_group
                ),
                joinedload(self._model.fields).joinedload(AssetTypeCategoryField.options),
            )
            .join(User, User.id == self._model.user_id)
            .join(Location, Location.id == User.location_id)
            .where(Location.organization_id == organization_id)
            .order_by(sort_order[sort_by])
        )

        if q:
            filters = BaseRepository.parse_filters(model=self._model, name__ilike=f"%{q}%")
            select_query = select_query.filter(*filters)

        return await apaginate(
            self.repository.session,
            select_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=CustomPage),
            transformer=lambda asset_type_categories: [
                AssetTypeCategoryResponse.convert(asset_type_category)
                for asset_type_category in asset_type_categories
            ],
        )

    async def get_asset_type_category(self, organization_id: int, asset_type_category_id: int):
        return await self.repository.get_one_or_none(
            join=[self._model.user, User.location, Location.organization],
            options=[
                joinedload(self._model.user)
                .joinedload(User.location)
                .joinedload(Location.organization),
                joinedload(self._model.fields),
                joinedload(self._model.fields).joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.fields).joinedload(
                    AssetTypeCategoryField.asset_type_category_group
                ),
            ],
            id=asset_type_category_id,
            organization_id=organization_id,
        )

    async def get_asset_type_categories(self, organization_id: int):
        stmt = (
            select(AssetTypeCategory)
            .join(AssetTypeCategory.user)
            .join(User.location)
            .join(Location.organization)
            .where(Organization.id == organization_id)
            .order_by(desc(AssetTypeCategory.id))
        )
        result = await self.repository.execute(stmt)
        return result.scalars().all()


def setup(app, session, *args, **kwargs):
    return app.add_service(AssetTypeCategoryService(app, session), session.info["session_id"])
