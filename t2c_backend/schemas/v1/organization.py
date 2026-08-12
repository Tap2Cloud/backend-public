from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from t2c_backend.models import Organization as OrganizationModel
from t2c_backend.schemas.v1.product_pass_type import ProductPassType


class DisplayOrganization(BaseModel):
    id: int
    name: str
    number: str | None
    logo: str | None
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(organization: OrganizationModel) -> "DisplayOrganization":
        return DisplayOrganization(
            id=organization.id,
            name=organization.name,
            number=organization.number,
            createdAt=int(organization.created_at.timestamp()),
            logo=organization.logo.get_string() if organization.logo is not None else None,
        )

    @staticmethod
    def to_orm(organization_obj: "DisplayOrganization") -> OrganizationModel:
        return OrganizationModel(
            id=organization_obj.id,
            name=organization_obj.name,
            number=organization_obj.number,
            created_at=datetime.fromtimestamp(organization_obj.created_at),
        )


class Organization(DisplayOrganization):
    product_pass_type: ProductPassType = Field(..., alias="productPassType")


class CreateOrganizationRequest(BaseModel):
    name: str
    number: str
    product_pass_type: ProductPassType = Field(..., alias="productPassType")

    model_config = ConfigDict(from_attributes=True)


class UpdateOrganizationRequest(BaseModel):
    name: str | None
    number: str | None

    model_config = ConfigDict(from_attributes=True)


class UpdateOrganizationResponse(BaseModel):
    id: int
    name: str | None
    number: str | None
    logo: str | None = None
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class DetailedOrganization(DisplayOrganization):
    location_count: int = Field(..., alias="locationCount")
    user_count: int = Field(..., alias="userCount")
    role_count: int = Field(..., alias="roleCount")

    model_config = ConfigDict(from_attributes=True)


class OrganizationDetails(DetailedOrganization):
    ...

    @staticmethod
    def from_model(organization) -> "OrganizationDetails":
        return OrganizationDetails(
            id=organization.id,
            name=organization.name,
            number=organization.number,
            createdAt=int(organization.created_at.timestamp()),
            logo=organization.logo.get_string() if organization.logo is not None else None,
            locationCount=organization.location_count,
            userCount=organization.user_count,
            roleCount=organization.role_count,
        )
