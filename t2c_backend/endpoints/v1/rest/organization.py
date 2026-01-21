from fastapi import APIRouter, Depends, File, Form, Path, Response, UploadFile

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.location import Location, LocationCreateRequest
from t2c_backend.schemas.v1.organization import (
    UpdateOrganizationResponse,
)
from t2c_backend.schemas.v1.role import RoleBase, RoleCreate
from t2c_backend.schemas.v1.taxonomy import Taxonomy
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.errors import UnAuthorizedError
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/organization", response_model=Location, status_code=200)
async def create_organization_with_location(
    name: str = Form(...),
    number: str = Form(...),
    email: str = Form(...),
    taxonomy: Taxonomy = Form(...),
    logo: UploadFile | None = File(None),
    location: LocationCreateRequest = Form(...),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    (
        org,
        location,
    ) = await services.organization_service.create_organization_with_location(
        name=name,
        number=number,
        email=email,
        taxonomy=Taxonomy.to_orm(taxonomy),
        logo=logo,
        location_data=location,
        user_id=token.user_id,
    )

    return Location.convert(location=location, organization=org)


@router.put("/organization", response_model=UpdateOrganizationResponse, status_code=200)
async def update_organization(
    name: str = Form(...),
    number: str | None = Form(None),
    email: str | None = Form(None),
    logo: UploadFile = File(None),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    organization = await services.organization_service.update_organization(
        token.organization_id,
        name=name,
        number=number,
        email=email,
        logo=logo,
    )

    return UpdateOrganizationResponse(
        id=organization.id,
        name=organization.name,
        number=organization.number,
        email=organization.email,
        logo=organization.logo.get_string() if organization.logo else None,
        createdAt=int(organization.created_at.timestamp()),
    )


@router.get("/organization/roles", response_model=list[RoleBase], status_code=200)
async def get_organization_roles(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    if token.organization_id is None:
        raise UnAuthorizedError(msg="Unauthorized to get roles.")

    roles = await services.role_service.get_roles_by_organisation_id(
        organization_id=token.organization_id,
    )

    return RoleBase.convert(roles=roles)


@router.post("/organization/roles", response_model=RoleBase, status_code=200)
async def create_organization_roles(
    role_data: RoleCreate,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    if token.organization_id is None:
        raise UnAuthorizedError(msg="Unauthorized to create role.")

    role = await services.role_service.create_role_by_organisation_id(
        organization_id=token.organization_id,
        role_data=role_data,
    )

    return RoleBase.convert_(role=role)


@router.delete("/organization/{organizationId}", status_code=200)
async def delete_organization(
    organization_id: int = Path(..., alias="organizationId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.organization_service.delete_organization(organization_id)
    return Response(status_code=200)
