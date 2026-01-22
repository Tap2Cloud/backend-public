import json
import uuid

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from t2c_backend.models import TypeplateImage as TypeplateImageModel
from t2c_backend.schemas.v1.documents import DocumentResponse


class TypeplateRequest(BaseModel):
    test_results: str | None = Field(..., alias="testResults")
    eu_id: str | None = Field(..., alias="euId")
    carbon_footprint_label: str | None = Field(..., alias="carbonFootprintLabel")

    model_config = ConfigDict(from_attributes=True)


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


class TypeplateImageRequest(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


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


class TypeplateResponse(BaseModel):
    id: int
    test_results: str | None = Field(..., alias="testResults")
    eu_id: str | None = Field(..., alias="euId")
    carbon_footprint_label: str | None = Field(..., alias="carbonFootprintLabel")
    eu_file_id: uuid.UUID | None = Field(..., alias="euFileId")
    eu_file: DocumentResponse | None = Field(..., alias="euFile")
    typeplate_images: list[TypeplateImage] | None = Field(..., alias="typeplateImages")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(fields, eu_file_data, typeplate_images) -> "TypeplateResponse":
        return TypeplateResponse(
            id=fields.id,
            testResults=fields.test_results,
            euId=fields.eu_id,
            carbonFootprintLabel=fields.carbon_footprint_label,
            euFileId=fields.eu_file_id or None,
            euFile=DocumentResponse.convert(eu_file_data) if eu_file_data is not None else None,
            typeplateImages=[TypeplateImage.from_model(img) for img in typeplate_images],
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
