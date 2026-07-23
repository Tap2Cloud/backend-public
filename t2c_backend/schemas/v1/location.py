import json

from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.datastructures import UploadFile

from t2c_backend.models import Location as LocationModel
from t2c_backend.models import Organization as OrganizationModel
from t2c_backend.schemas.v1.organization import DisplayOrganization, Organization
from t2c_backend.schemas.v1.taxonomy import Taxonomy


class LocationCreateRequest(BaseModel):
    name: str
    street: str | None
    postcode: str | None
    city: str
    country: str
    region: str | None
    tel_number: str | None = Field(..., alias="telNumber")
    mobile_number: str = Field(..., alias="mobileNumber")
    fax_number: str | None = Field(..., alias="faxNumber")
    email: str

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
            name=location.name,
            id=location.id,
            street=location.street,
            postcode=location.postcode,
            city=location.city,
            country=location.country,
            region=location.region,
            telNumber=location.tel_number,
            mobileNumber=location.mobile_number,
            faxNumber=location.fax_number,
            email=location.email,
            organization=Organization(
                id=organization.id,
                name=organization.name,
                number=organization.number,
                email=organization.email,
                logo=organization.logo.get_string() if organization.logo is not None else None,
                createdAt=int(organization.created_at.timestamp()),
                taxonomy=Taxonomy.from_model(organization.taxonomy),
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
            name=location.name,
            id=location.id,
            street=location.street,
            postcode=location.postcode,
            city=location.city,
            country=location.country,
            region=location.region,
            telNumber=location.tel_number,
            mobileNumber=location.mobile_number,
            faxNumber=location.fax_number,
            email=location.email,
            organization=Organization(
                id=organization.id,
                name=organization.name,
                number=organization.number,
                email=organization.email,
                createdAt=int(organization.created_at.timestamp()),
                taxonomy=Taxonomy.from_model(organization.taxonomy),
                logo=organization.logo.get_string() if organization.logo is not None else None,
            ),
        )
