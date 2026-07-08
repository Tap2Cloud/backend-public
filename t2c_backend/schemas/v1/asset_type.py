import json
import uuid

from pydantic import BaseModel, ConfigDict, conlist, model_validator
from pydantic import Field as PydanticField
from utils.misc import is_valid_gtin

from t2c_backend.models import AssetType as AssetTypeModel
from t2c_backend.models import AssetTypeField as AssetTypeFieldModel
from t2c_backend.models import AssetTypeFieldOptions as AssetTypeFieldOptionsModel
from t2c_backend.schemas.v1.asset_type_category import DisplayAssetTypeCategory, Field
from t2c_backend.schemas.v1.typeplates import (
    TypeplateImageRequest,
    TypeplateRequest,
    TypeplateResponse,
)


class BaseFieldOptions(BaseModel):
    option_id: int = PydanticField(..., alias="optionId")

    model_config = ConfigDict(from_attributes=True)


class BaseField(BaseModel):
    field_id: int = PydanticField(..., alias="fieldId")
    response_value: str = PydanticField(..., alias="responseValue")
    asset_type_field_options: list["BaseFieldOptions"] = PydanticField(
        default=[], alias="assetTypeFieldOptions"
    )

    model_config = ConfigDict(from_attributes=True)


class CreateAssetTypeRequest(BaseModel):
    name: str
    video_links: str | None = PydanticField(..., alias="videoLinks")
    video_title: str | None = PydanticField(..., alias="videoTitle")
    web_link: str | None = PydanticField(..., alias="webLink")
    web_link_title: str | None = PydanticField(..., alias="webLinkTitle")
    description: str
    weight: float | None
    manufacturer: str | None
    gtin: str | None
    asset_type_category_id: int = PydanticField(..., alias="assetTypeCategoryId")
    fields: conlist(BaseField, min_length=1)
    typeplate_details: TypeplateRequest = PydanticField(None, alias="typeplateDetails")
    typeplate_images: list[TypeplateImageRequest] | None = PydanticField(
        None, alias="typeplateImages"
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return json.loads(value.file.read())

    @model_validator(mode="after")
    @classmethod
    def validate_json(cls, value):
        if value.gtin and not is_valid_gtin(value.gtin):
            raise ValueError("Invalid GTIN format")
        return value


class UpdateAssetTypeRequest(BaseModel):
    name: str
    video_links: str | None = PydanticField(..., alias="videoLinks")
    video_title: str | None = PydanticField(..., alias="videoTitle")
    web_link: str | None = PydanticField(..., alias="webLink")
    web_link_title: str | None = PydanticField(..., alias="webLinkTitle")
    description: str
    weight: float | None
    manufacturer: str | None
    gtin: str | None
    fields: conlist(BaseField, min_length=1)

    @model_validator(mode="after")
    @classmethod
    def validate_json(cls, value):
        if value.gtin and not is_valid_gtin(value.gtin):
            raise ValueError("Invalid GTIN format")
        return value


class AssetTypeFieldOptions(BaseFieldOptions):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(field_option: list["AssetTypeFieldOptionsModel"]) -> list["AssetTypeFieldOptions"]:
        return [AssetTypeFieldOptions(id=ffo.id, optionId=ffo.option_id) for ffo in field_option]


class AssetTypeField(BaseModel):
    id: int
    field_id: int = PydanticField(alias="fieldId")
    response_value: str = PydanticField(alias="responseValue")
    asset_type_field_options: list["AssetTypeFieldOptions"] = PydanticField(
        alias="assetTypeFieldOptions"
    )

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(field: AssetTypeFieldModel) -> "AssetTypeField":
        return AssetTypeField(
            id=field.id,
            fieldId=field.field_id,
            responseValue=field.response_value,
            assetTypeFieldOptions=AssetTypeFieldOptions.convert(field.asset_type_field_options),
        )

    @staticmethod
    def from_list(fields: list["AssetTypeFieldModel"]) -> list["AssetTypeField"]:
        return [AssetTypeField.from_model(ff) for ff in fields]


class FormData(BaseModel):
    fields: Field
    values: AssetTypeField

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset_type_field) -> "FormData":
        return FormData(
            fields=Field.from_model(asset_type_field.asset_type_category_field),
            values=AssetTypeField.from_model(asset_type_field),
        )


class AssetTypeDocument(BaseModel):
    id: uuid.UUID
    name: str
    content_type: str = PydanticField(..., alias="contentType")
    created_at: int = PydanticField(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset_type_document) -> "AssetTypeDocument":
        return AssetTypeDocument(
            id=asset_type_document.id,
            name=asset_type_document.name,
            contentType=asset_type_document.content_type,
            createdAt=int(asset_type_document.created_at.timestamp()),
        )


class AssetTypeResponse(BaseModel):
    id: int
    name: str
    video_links: str | None = PydanticField(alias="videoLinks")
    video_title: str | None = PydanticField(alias="videoTitle")
    web_link: str | None = PydanticField(alias="webLink")
    web_link_title: str | None = PydanticField(alias="webLinkTitle")
    description: str
    weight: float | None
    manufacturer: str | None
    gtin: str | None
    form: conlist(FormData, min_length=1)
    instruction_manuals: list[AssetTypeDocument] = PydanticField(None, alias="instructionManuals")
    asset_type_category: DisplayAssetTypeCategory = PydanticField(alias="assetTypeCategory")
    typeplates: TypeplateResponse | None = PydanticField(None)

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(
        asset_type,
        instruction_manuals_data,
    ) -> "AssetTypeResponse":
        atr = AssetTypeResponse(
            id=asset_type.id,
            name=asset_type.name,
            videoLinks=asset_type.video_links,
            videoTitle=asset_type.video_title,
            webLink=asset_type.web_link,
            webLinkTitle=asset_type.web_link_title,
            description=asset_type.description,
            weight=asset_type.weight,
            manufacturer=asset_type.manufacturer,
            gtin=asset_type.gtin,
            form=[FormData.from_model(atf) for atf in asset_type.fields],
            instructionManuals=[
                AssetTypeDocument.from_model(doc) for doc in instruction_manuals_data
            ],
            assetTypeCategory=DisplayAssetTypeCategory.from_model(asset_type.asset_type_category),
            typeplates=TypeplateResponse.convert(
                asset_type.typeplate,
                asset_type.typeplate.documents,
                [img.typeplate_image for img in asset_type.typeplate.typeplate_images],
            )
            if asset_type.typeplate
            else None,
        )

        return atr


class DisplayAssetType(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(category: AssetTypeModel) -> "DisplayAssetType":
        return DisplayAssetType(
            id=category.id,
            name=category.name,
            description=category.description,
        )

    @staticmethod
    def to_orm(category: "DisplayAssetType") -> AssetTypeModel:
        return AssetTypeModel(
            **category.model_dump(),
        )


class InstructionManualAssetTypeResponse(BaseModel):
    id: int
    name: str
    video_link: str | None = PydanticField(..., alias="videoLink")
    video_title: str | None = PydanticField(..., alias="videoTitle")
    web_link: str | None = PydanticField(..., alias="webLink")
    web_link_title: str | None = PydanticField(..., alias="webLinkTitle")
    description: str
    instruction_manuals: list[AssetTypeDocument] = PydanticField(..., alias="instructionManuals")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(
        asset_type,
        instruction_manuals_data,
    ) -> "InstructionManualAssetTypeResponse":
        return InstructionManualAssetTypeResponse(
            id=asset_type.id,
            name=asset_type.name,
            videoLink=asset_type.video_links,
            videoTitle=asset_type.video_title,
            webLink=asset_type.web_link,
            webLinkTitle=asset_type.web_link_title,
            description=asset_type.description,
            instructionManuals=[
                AssetTypeDocument.from_model(doc) for doc in instruction_manuals_data
            ],
        )


class SelectiveFilters(BaseModel):
    categories: list[DisplayAssetTypeCategory] | None = None
