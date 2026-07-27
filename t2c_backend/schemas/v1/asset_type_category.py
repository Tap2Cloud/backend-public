from typing import Any

from pydantic import BaseModel, ConfigDict, conlist, model_validator
from pydantic import Field as PydanticField

from t2c_backend.models import AssetTypeCategory as AssetTypeCategoryModel
from t2c_backend.models import AssetTypeCategoryField as AssetTypeCategoryFieldModel
from t2c_backend.models import AssetTypeCategoryFieldOption as AssetTypeCategoryFieldOptionModel
from t2c_backend.models import AssetTypeCategoryGroup as AssetTypeCategoryGroupModel
from t2c_backend.schemas.v1.user import DisplayUser
from t2c_backend.utils.enums import InputType


class AssetTypeCategoryGroupResponse(BaseModel):
    id: int
    name: str
    order: int

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(group: AssetTypeCategoryGroupModel) -> "AssetTypeCategoryGroupResponse":
        return AssetTypeCategoryGroupResponse(
            id=group.id,
            name=group.name,
            order=group.order,
        )

    @staticmethod
    def from_list(
        groups: list[AssetTypeCategoryGroupModel],
    ) -> list["AssetTypeCategoryGroupResponse"]:
        return [AssetTypeCategoryGroupResponse.from_model(group) for group in groups]


class BaseFieldOption(BaseModel):
    option_id: str = PydanticField(..., alias="optionId")
    option_label: str = PydanticField(..., alias="optionLabel")

    model_config = ConfigDict(from_attributes=True)


class BaseField(BaseModel):
    field_name: str = PydanticField(..., alias="fieldName")
    field_place_holder: str | None = PydanticField(..., alias="fieldPlaceHolder")
    field_display_name: str = PydanticField(..., alias="fieldDisplayName")
    field_is_required: bool = PydanticField(..., alias="fieldIsRequired")
    field_order: int = PydanticField(..., alias="fieldOrder")
    field_type: InputType = PydanticField(..., alias="fieldType")
    field_group_id: int = PydanticField(..., alias="fieldGroupId")
    options: list["BaseFieldOption"]

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def check_options(cls, data: Any) -> Any:
        field_type = data.get("fieldType")
        options = data.get("options", [])
        field_order = data.get("fieldOrder")

        if field_type in ["text", "number"] and options:
            raise ValueError(f"`options` must be empty for field type '{field_type}'.")
        if field_type in ["radio", "multiselect"] and len(options) <= 1:
            raise ValueError(
                f"`options` must have more than one item for field type '{field_type}'.",
            )
        if field_order <= 0:
            raise ValueError("fieldOrder must be greater than 0.")

        return data

    model_config = ConfigDict(from_attributes=True)


class CreateAssetTypeCategoryRequest(BaseModel):
    name: str
    has_typeplates: bool = PydanticField(..., alias="hasTypeplates")
    fields: conlist(BaseField, min_length=1)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def check_fields(cls, data: Any) -> Any:
        seen_orders, seen_names = set(), set()
        for field in data["fields"]:
            field_order = field.get("fieldOrder")
            field_name = field.get("fieldName")
            if field_order in seen_orders:
                raise ValueError(f"Multiple fields have the same field order '{field_order}'.")
            if field_name in seen_names:
                raise ValueError(f"Multiple fields have the same field name '{field_name}'.")
            seen_orders.add(field_order)
            seen_names.add(field_name)
        return data

    model_config = ConfigDict(from_attributes=True)


class UpdateBaseFieldOption(BaseModel):
    id: int
    option_id: str | None = PydanticField(None, alias="optionId")
    option_label: str | None = PydanticField(None, alias="optionLabel")

    model_config = ConfigDict(from_attributes=True)


class UpdateBaseFields(BaseModel):
    id: int
    field_name: str | None = PydanticField(None, alias="fieldName")
    field_place_holder: str | None = PydanticField(None, alias="fieldPlaceHolder")
    field_display_name: str | None = PydanticField(None, alias="fieldDisplayName")
    field_order: int | None = PydanticField(None, alias="fieldOrder")
    asset_type_category_group_id: int | None = PydanticField(None, alias="fieldGroupId")
    options: list["UpdateBaseFieldOption"]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def check_options(cls, data: Any) -> Any:
        field_order = data.get("fieldOrder")
        if field_order <= 0:
            raise ValueError("fieldOrder must be greater than 0.")

        return data


class UpdateAssetTypeCategoryRequest(BaseModel):
    name: str | None
    fields: conlist(UpdateBaseFields, min_length=1)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def check_fields(cls, data: Any) -> Any:
        seen_orders, seen_names = set(), set()
        for field in data["fields"]:
            field_order = field.get("fieldOrder")
            field_name = field.get("fieldName")
            if field_order in seen_orders:
                raise ValueError(f"Multiple fields have the same field order '{field_order}'.")
            if field_name in seen_names:
                raise ValueError(f"Multiple fields have the same field name '{field_name}'.")
            seen_orders.add(field_order)
            seen_names.add(field_name)
        return data

    model_config = ConfigDict(from_attributes=True)


class FieldOption(BaseFieldOption):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(field_options: list["AssetTypeCategoryFieldOptionModel"]) -> list["FieldOption"]:
        return [
            FieldOption(id=ffo.id, optionId=ffo.option_id, optionLabel=ffo.option_label)
            for ffo in field_options
        ]


class Field(BaseModel):
    id: int
    field_name: str = PydanticField(..., alias="fieldName")
    field_place_holder: str = PydanticField(..., alias="fieldPlaceHolder")
    field_display_name: str = PydanticField(..., alias="fieldDisplayName")
    field_is_required: bool = PydanticField(..., alias="fieldIsRequired")
    field_order: int = PydanticField(..., alias="fieldOrder")
    field_type: InputType = PydanticField(..., alias="fieldType")
    options: list["FieldOption"]
    field_group: AssetTypeCategoryGroupResponse = PydanticField(..., alias="fieldGroup")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset_type_category_field: AssetTypeCategoryFieldModel) -> "Field":
        return Field(
            id=asset_type_category_field.id,
            fieldName=asset_type_category_field.field_name,
            fieldPlaceHolder=asset_type_category_field.field_place_holder,
            fieldDisplayName=asset_type_category_field.field_display_name,
            fieldIsRequired=asset_type_category_field.field_is_required,
            fieldOrder=asset_type_category_field.field_order,
            fieldType=asset_type_category_field.field_type,
            options=FieldOption.convert(asset_type_category_field.options),
            fieldGroup=AssetTypeCategoryGroupResponse.from_model(
                asset_type_category_field.asset_type_category_group
            ),
        )

    @staticmethod
    def from_list(fields: list["AssetTypeCategoryFieldModel"]) -> list["Field"]:
        return [Field.from_model(ff) for ff in fields]


class AssetTypeCategoryResponse(BaseModel):
    id: int
    name: str
    has_typeplates: bool = PydanticField(..., alias="hasTypeplates")
    fields: conlist(Field, min_length=1)
    user: DisplayUser | None
    created_at: int = PydanticField(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(category: AssetTypeCategoryModel) -> "AssetTypeCategoryResponse":
        return AssetTypeCategoryResponse(
            id=category.id,
            name=category.name,
            hasTypeplates=category.has_typeplates,
            fields=Field.from_list(category.fields),
            user=DisplayUser.convert(category.user) if category.user else None,
            createdAt=int(category.created_at.timestamp()),
        )


class DisplayAssetTypeCategory(BaseModel):
    id: int
    name: str
    has_typeplates: bool = PydanticField(..., alias="hasTypeplates")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(category: AssetTypeCategoryModel) -> "DisplayAssetTypeCategory":
        return DisplayAssetTypeCategory(
            id=category.id,
            name=category.name,
            hasTypeplates=category.has_typeplates,
        )
