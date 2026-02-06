from fastapi import APIRouter, Depends

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.models import Role
from t2c_backend.schemas.v1.location import LocationBaseResponse, LocationCreateRequest
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.user import (
    UserAcceptInviteRequest,
    UserInviteRequest,
    UserInviteResponse,
    UserReInviteRequest,
    UserRejectInviteRequest,
    UserResponse,
)
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.put("/location", response_model=LocationBaseResponse, status_code=200)
async def update_location(
    location_data: LocationCreateRequest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    location = await services.location_service.update_location(
        token.location_id,
        location_data,
    )

    return LocationBaseResponse.convert(location, location.organization)


@router.get(
    "/filter/location",
    response_model=list[LocationBaseResponse],
    status_code=200,
)
async def list_location(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return [
        LocationBaseResponse.convert(location, location.organization)
        for location in await services.location_service.list_location(
            organization_id=token.organization_id
        )
    ]


@router.post("/location/user/invite", response_model=UserInviteResponse, status_code=201)
async def location_user_invite(
    invite_data: UserInviteRequest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    user_invite_response = await services.location_service.location_invite_user(
        token.user_id,
        invite_data.email,
        invite_data.location.id,
        Role.convert(invite_data.roles, organization_id=token.organization_id),
    )

    return UserInviteResponse.convert(user_invite_response, invite_data.roles, invite_data.location)


@router.post("/location/user/invite/accept", response_model=UserResponse, status_code=200)
async def location_user_invite_accept(
    accept_invite_data: UserAcceptInviteRequest,
    services: DictContainer = Depends(get_services),
):
    return UserResponse.convert(
        await services.location_service.location_accept_invite_user(accept_invite_data)
    )


@router.post("/location/user/invite/reject", status_code=200)
async def location_user_invite_reject(
    reject_invite_data: UserRejectInviteRequest,
    services: DictContainer = Depends(get_services),
):
    await services.location_service.location_reject_invite_user(reject_invite_data.token)


@router.post("/location/user/re-invite", status_code=200)
async def location_user_re_invite(
    re_invite_data: UserReInviteRequest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.location_service.location_re_invite_user(re_invite_data.token)
