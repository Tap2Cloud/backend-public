from fastapi import APIRouter, Depends, File, Form, Path, Query, Response, UploadFile

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.user import (
    ChangePasswordRequest,
    OrganizationUser,
    OrganizationUsersCustomPage,
    UserResponse,
)
from t2c_backend.services import get_services
from t2c_backend.utils.enums import UserStatus
from t2c_backend.utils.errors import NotFoundError, UnAuthenticatedError
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.delete("/user/{cascadeOrg}", operation_id="delete user")
async def delete_user_handler(
    cascade_org: bool = Path(..., alias="cascadeOrg"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"user_delete": True})),
    services: DictContainer = Depends(get_services),
):
    if cascade_org and not {"organization_delete"}.issubset(
        JWTAPIAccessTokenBearer.user_permissions(token)
    ):
        raise UnAuthenticatedError("Insufficient permissions.")

    await services.user_service.delete_user(token.user_id, token.organization_id, cascade_org)
    return Response(status_code=204)


@router.delete(
    "/organization/user/{userId}/{cascadeOrg}", operation_id="delete user by id", status_code=200
)
async def delete_user(
    user_id: int = Path(..., alias="userId"),
    cascade_org: bool = Path(..., alias="cascadeOrg"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"org_user_delete": True})),
    services: DictContainer = Depends(get_services),
):
    if cascade_org and not {"organization_delete"}.issubset(
        JWTAPIAccessTokenBearer.user_permissions(token)
    ):
        raise UnAuthenticatedError("Insufficient permissions.")

    await services.user_service.delete_user(user_id, token.organization_id, cascade_org)
    return Response(status_code=200)


@router.get("/user/profile", operation_id="get user profile", response_model=UserResponse)
async def user_profile_handler(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    user = await services.user_service.get_user_profile(
        token.user_id,
    )

    return UserResponse.convert(user)


@router.put("/user/profile/", operation_id="update user profile", response_model=UserResponse)
async def user_profile_update_handler(
    picture: UploadFile = File(None),
    first_name: str = Form(..., alias="firstName", validation_alias="firstName"),
    last_name: str = Form(..., alias="lastName", validation_alias="lastName"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"user_update": True})),
    services: DictContainer = Depends(get_services),
):
    user = await services.user_service.update_user_profile(
        token.user_id,
        picture,
        first_name,
        last_name,
    )

    if not user:
        raise NotFoundError(msg="User not found")

    return UserResponse.convert(user)


@router.get(
    "/organization/users",
    operation_id="get organization users",
    response_model=OrganizationUsersCustomPage[OrganizationUser],
    status_code=200,
)
async def organization_users_handler(
    query: str | None = None,
    roles: list[str] = Query(None),
    status: UserStatus | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"user_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.user_service.organization_user_handler(
        query=query,
        roles=roles,
        status=status,
        page=page,
        page_size=page_size,
        organization_id=token.organization_id,
    )


@router.post("/user/password/change", operation_id="change password", name="change-user-password")
async def change_user_password(
    passwords: ChangePasswordRequest,
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"change_user_password": True})
    ),
    services: DictContainer = Depends(get_services),
):
    await services.user_service.change_password(
        old_password=passwords.old_password,
        new_password=passwords.new_password,
        user_id=token.user_id,
    )
    return Response(status_code=200)
