import json

from pydantic import BaseModel, ConfigDict, model_validator
from starlette.datastructures import UploadFile

from t2c_backend.models import Location as LocationModel
from t2c_backend.models import Organization as OrganizationModel
from t2c_backend.schemas.v1.organization import DisplayOrganization, Organization
from t2c_backend.schemas.v1.product_pass_type import ProductPassType


class LocationCreateRequest(BaseModel):
    city: str
    country: str

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


class LocationUpdateRequest(LocationCreateRequest):
    pass


class LocationBaseResponse(LocationCreateRequest):
    id: int
    organization: Organization

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(
        location: LocationModel,
        organization: OrganizationModel,
    ) -> "LocationBaseResponse":
        return LocationBaseResponse(
            id=location.id,
            city=location.city,
            country=location.country,
            organization=Organization(
                id=organization.id,
                name=organization.name,
                number=organization.number,
                logo=organization.logo.get_string() if organization.logo is not None else None,
                createdAt=int(organization.created_at.timestamp()),
                productPassType=ProductPassType.from_model(organization.product_pass_type),
            ),
        )

    @staticmethod
    def to_orm(location_obj: "LocationBaseResponse") -> LocationModel:
        return LocationModel(
            **location_obj.model_dump(exclude={"organization"}),
            organization=DisplayOrganization.to_orm(location_obj.organization),
        )


class Location(LocationBaseResponse):
    organization: Organization

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(location: LocationModel, organization: OrganizationModel) -> "Location":
        return Location(
            id=location.id,
            city=location.city,
            country=location.country,
            organization=Organization(
                id=organization.id,
                name=organization.name,
                number=organization.number,
                createdAt=int(organization.created_at.timestamp()),
                productPassType=ProductPassType.from_model(organization.product_pass_type),
                logo=organization.logo.get_string() if organization.logo is not None else None,
            ),
        )
