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

    async def create_asset_type_category(self, user_id: int, location_id: int, form_data: dict):
        form = AssetTypeCategory(
            user_id=user_id,
            location_id=location_id,
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
        location_id: int,
    ):
        db_asset_type_details = await self.repository.get_one_or_none(
            id=asset_type_category_id,
            options=[joinedload(self._model.user)],
        )
        if not db_asset_type_details or db_asset_type_details.location_id != location_id:
            raise NotFoundError("Asset type category not found")

        for key, value in updated_asset_type_category_data.model_dump(
            exclude={"fields"}, exclude_none=True
        ).items():
            setattr(db_asset_type_details, key, value)

        incoming_field_ids = {
            field.id for field in updated_asset_type_category_data.fields if field.id is not None
        }
        fields_to_remove = [
            field
            for field in db_asset_type_details.fields
            if field.id not in incoming_field_ids and field.id is not None
        ]
        for field in fields_to_remove:
            db_asset_type_details.fields.remove(field)
        await self.repository.save(db_asset_type_details)

        for category_field in updated_asset_type_category_data.fields:
            if not await self.asset_type_category_groups_repository.get_one_or_none(
                id=category_field.asset_type_category_group_id
            ):
                raise NotFoundError("Asset type category group not found")
            if category_field.id is None:
                new_field = AssetTypeCategoryField(
                    field_name=category_field.field_name,
                    field_place_holder=category_field.field_place_holder,
                    field_display_name=category_field.field_display_name,
                    field_order=-category_field.field_order,
                    field_type=category_field.field_type,
                    field_is_required=category_field.field_is_required,
                    asset_type_category_group_id=category_field.asset_type_category_group_id,
                    asset_type_category_id=db_asset_type_details.id,
                )
                for option in category_field.options:
                    new_field.options.append(
                        AssetTypeCategoryFieldOption(
                            option_id=option.option_id,
                            option_label=option.option_label,
                        )
                    )
                db_asset_type_details.fields.append(new_field)
            else:
                asset_type_category_field = next(
                    (f for f in db_asset_type_details.fields if f.id == category_field.id),
                    None,
                )

                if not asset_type_category_field:
                    raise NotFoundError("Asset type category field not found")
                if category_field.field_type != asset_type_category_field.field_type:
                    raise BadRequestError("Field type cannot be changed")

                for key, value in category_field.model_dump(
                    exclude={"id", "options", "field_type"}
                ).items():
                    if key == "field_order":
                        setattr(asset_type_category_field, key, -value)
                    else:
                        setattr(asset_type_category_field, key, value)

                incoming_option_ids = {
                    option.id for option in category_field.options if option.id is not None
                }
                options_to_remove = [
                    option
                    for option in asset_type_category_field.options
                    if option.id is not None and option.id not in incoming_option_ids
                ]
                for option in options_to_remove:
                    asset_type_category_field.options.remove(option)
                await self.repository.save(asset_type_category_field)
                for option_data in category_field.options:
                    if option_data.id is None:
                        asset_type_category_field.options.append(
                            AssetTypeCategoryFieldOption(
                                option_id=option_data.option_id,
                                option_label=option_data.option_label,
                            )
                        )
                    else:
                        existing_option = next(
                            (
                                o
                                for o in asset_type_category_field.options
                                if o.id == option_data.id
                            ),
                            None,
                        )
                        if existing_option is None:
                            raise NotFoundError("Asset type category field option not found")
                        for key, value in option_data.model_dump(
                            exclude={"id"}, exclude_unset=True
                        ).items():
                            setattr(existing_option, key, value)
        all_field_orders = []
        for field in db_asset_type_details.fields:
            normalized_order = abs(field.field_order)
            if normalized_order in all_field_orders:
                raise BadRequestError("Duplicate field order found")
            all_field_orders.append(normalized_order)
            field.field_order = normalized_order
        await self.repository.save(db_asset_type_details)
        db_asset_type_details = await self.repository.get_one_or_none(
            id=asset_type_category_id,
            options=[
                joinedload(self._model.user),
                joinedload(self._model.user).joinedload(User.location),
            ],
        )
        return db_asset_type_details

    async def get_asset_type_category_by_id(self, asset_type_category_id: int, location_id: int):
        return await self.repository.get_one_or_none(
            location_id=location_id, id=asset_type_category_id
        )

    async def delete_asset_type_category(self, asset_type_category_id: int, location_id: int):
        db_asset_type_category = await self.repository.get_one_or_none(id=asset_type_category_id)
        if not db_asset_type_category or db_asset_type_category.location_id != location_id:
            raise NotFoundError("Asset type category not found")
        return await self.repository.delete(id=asset_type_category_id)

    async def list_asset_type_category(self, location_id: int):
        stmt = (
            select(AssetTypeCategory)
            .where(AssetTypeCategory.location_id == location_id)
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
        location_id: int,
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
            .where(self._model.location_id == location_id)
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

    async def get_asset_type_category(self, location_id: int, asset_type_category_id: int):
        return await self.repository.get_one_or_none(
            options=[
                joinedload(self._model.user),
                joinedload(self._model.fields),
                joinedload(self._model.fields).joinedload(AssetTypeCategoryField.options),
                joinedload(self._model.fields).joinedload(
                    AssetTypeCategoryField.asset_type_category_group
                ),
            ],
            id=asset_type_category_id,
            location_id=location_id,
        )

    async def get_asset_type_categories(self, location_id: int):
        stmt = (
            select(AssetTypeCategory)
            .where(AssetTypeCategory.location_id == location_id)
            .order_by(desc(AssetTypeCategory.id))
        )
        result = await self.repository.execute(stmt)
        return result.scalars().all()


def setup(app, session, *args, **kwargs):
    return app.add_service(AssetTypeCategoryService(app, session), session.info["session_id"])
