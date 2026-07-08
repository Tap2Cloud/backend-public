import json
import uuid

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from t2c_backend.models import TypeplateImage as TypeplateImageModel


class TypeplateImageRequest(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TypeplateRequest(BaseModel):
    test_results: str | None = Field(..., alias="testResults")
    eu_id: str = Field(..., alias="euId")
    carbon_footprint_label: str | None = Field(..., alias="carbonFootprintLabel")

    model_config = ConfigDict(from_attributes=True)


class UpdateTypeplateRequest(BaseModel):
    test_results: str | None = Field(..., alias="testResults")
    eu_id: str = Field(..., alias="euId")
    carbon_footprint_label: str | None = Field(..., alias="carbonFootprintLabel")
    typeplate_images: list[TypeplateImageRequest] | None = Field(None, alias="typeplateImages")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return json.loads(value.file.read())


class TypeplateImage(BaseModel):
    id: uuid.UUID
    name: str
    image: str

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(typeplate_image: TypeplateImageModel) -> "TypeplateImage":
        return TypeplateImage(
            id=typeplate_image.id,
            name=typeplate_image.name,
            image=typeplate_image.image.get_string(),
        )


class TypeplateImageList(RootModel):
    root: list[TypeplateImageRequest]

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, UploadFile):
            return json.loads(value.file.read())
        return value


class TypeplateDocument(BaseModel):
    id: uuid.UUID
    name: str
    content_type: str = Field(..., alias="contentType")
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(typeplate_document) -> "TypeplateDocument":
        return TypeplateDocument(
            id=typeplate_document.id,
            name=typeplate_document.name,
            contentType=typeplate_document.content_type,
            createdAt=int(typeplate_document.created_at.timestamp()),
        )


class TypeplateResponse(BaseModel):
    id: int
    test_results: str | None = Field(..., alias="testResults")
    eu_id: str = Field(..., alias="euId")
    carbon_footprint_label: str | None = Field(..., alias="carbonFootprintLabel")
    eu_file: TypeplateDocument | None = Field(..., alias="euFile")
    typeplate_images: list[TypeplateImage] | None = Field(..., alias="typeplateImages")
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(fields, eu_file_data, typeplate_images) -> "TypeplateResponse":
        return TypeplateResponse(
            id=fields.id,
            testResults=fields.test_results,
            euId=fields.eu_id,
            carbonFootprintLabel=fields.carbon_footprint_label,
            typeplateImages=[TypeplateImage.from_model(img) for img in typeplate_images],
            euFile=TypeplateDocument.from_model(eu_file_data[0]) if len(eu_file_data) > 0 else None,
            createdAt=int(fields.created_at.timestamp()),
        )


class AssetTypeTypeplateResponse(BaseModel):
    id: int
    name: str
    description: str
    typeplate_details: TypeplateResponse = Field(..., alias="typeplateDetails")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(asset_type, eu_file_data, typeplate_documents) -> "AssetTypeTypeplateResponse":
        return AssetTypeTypeplateResponse(
            id=asset_type.id,
            name=asset_type.name,
            description=asset_type.description,
            typeplateDetails=TypeplateResponse.convert(
                asset_type.typeplate, eu_file_data, typeplate_documents
            )
            if asset_type.typeplate is not None
            else None,
        )
