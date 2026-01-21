from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from t2c_backend.models import Organization as OrganizationModel
from t2c_backend.schemas.v1.taxonomy import Taxonomy


class DisplayOrganization(BaseModel):
    id: int
    name: str
    number: str
    email: str
    logo: str | None
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(organization: OrganizationModel) -> "DisplayOrganization":
        return DisplayOrganization(
            id=organization.id,
            name=organization.name,
            number=organization.number,
            email=organization.email,
            createdAt=int(organization.created_at.timestamp()),
            logo=organization.logo.get_string() if organization.logo is not None else None,
        )

    @staticmethod
    def to_orm(organization_obj: "DisplayOrganization") -> OrganizationModel:
        return OrganizationModel(
            id=organization_obj.id,
            name=organization_obj.name,
            number=organization_obj.number,
            email=organization_obj.email,
            created_at=datetime.fromtimestamp(organization_obj.created_at),
        )


class Organization(DisplayOrganization):
    taxonomy: Taxonomy


class CreateOrganizationRequest(BaseModel):
    name: str
    number: str
    email: str
    taxonomy: Taxonomy

    model_config = ConfigDict(from_attributes=True)


class UpdateOrganizationRequest(BaseModel):
    name: str | None
    number: str | None
    email: str | None

    model_config = ConfigDict(from_attributes=True)


class UpdateOrganizationResponse(BaseModel):
    id: int
    name: str | None
    number: str | None
    email: str | None
    logo: str | None = None
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class DetailedOrganization(DisplayOrganization):
    location_count: int = Field(..., alias="locationCount")
    user_count: int = Field(..., alias="userCount")
    role_count: int = Field(..., alias="roleCount")

    model_config = ConfigDict(from_attributes=True)


class OrganizationCredit(BaseModel):
    credits: float
    hold_credits: float = Field(..., alias="holdCredits")

    model_config = ConfigDict(from_attributes=True)
