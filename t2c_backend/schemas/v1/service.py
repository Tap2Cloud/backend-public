from pydantic import BaseModel, ConfigDict, Field, model_validator

from t2c_backend.models.service import Service as ServiceModel
from t2c_backend.utils.enums import ServiceTypes
from t2c_backend.utils.errors import BadRequestError


class CreateService(BaseModel):
    service_name: str = Field(..., alias="serviceName")
    service_provider_name: str = Field(..., alias="serviceProviderName")
    contact: str
    expire_date: int = Field(..., alias="expireDate")
    service_date: int = Field(..., alias="serviceDate")
    service_type: str = Field(..., alias="serviceType")
    web: str | None
    email: str | None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, data):
        if data.get("expireDate") < data.get("serviceDate"):
            raise BadRequestError("expire date must be greater than service date")
        return data


class UpdateService(BaseModel):
    contact: str | None
    expire_date: int | None = Field(..., alias="expireDate")
    web: str | None
    email: str | None

    model_config = ConfigDict(from_attributes=True)


class ServiceResponse(BaseModel):
    id: int
    service_name: str = Field(..., alias="serviceName")
    service_provider_name: str = Field(..., alias="serviceProviderName")
    contact: str
    expire_date: int = Field(..., alias="expireDate")
    service_date: int = Field(..., alias="serviceDate")
    service_type: ServiceTypes = Field(..., alias="serviceType")
    web: str | None
    email: str | None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(service_data: ServiceModel) -> "ServiceResponse":
        return ServiceResponse(
            id=service_data.id,
            serviceName=service_data.service_name,
            serviceProviderName=service_data.service_provider_name,
            contact=service_data.contact,
            expireDate=int(service_data.expire_date.timestamp()),
            serviceDate=int(service_data.service_date.timestamp()),
            serviceType=ServiceTypes(service_data.service_type),
            web=service_data.web,
            email=service_data.email,
        )


class AssetServiceResponse(BaseModel):
    id: int
    manufacturing_date: int = Field(..., alias="manufacturingDate")
    asset_type_name: str = Field(..., alias="assetTypeName")
    asset_type_description: str = Field(..., alias="assetTypeDescription")
    serial_no: str | None = Field(..., alias="serialNo")
    services: list[ServiceResponse]

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(asset) -> "AssetServiceResponse":
        return AssetServiceResponse(
            id=asset.id,
            manufacturingDate=int(asset.manufacturing_date.timestamp()),
            assetTypeName=asset.asset_type.name,
            assetTypeDescription=asset.asset_type.description,
            serialNo=asset.serial_no,
            services=[ServiceResponse.convert(service) for service in asset.services],
        )
