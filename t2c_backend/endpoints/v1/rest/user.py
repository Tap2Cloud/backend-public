from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from pydantic import EmailStr

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.user import (
    ChangePasswordRequest,
    UserResponse,
)
from t2c_backend.services import get_services
from t2c_backend.utils.errors import NotFoundError
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.delete("/user")
async def delete_user_handler(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.user_service.delete_user(token.user_id, token.location_id)
    return Response(status_code=204)


@router.put("/user/profile/", response_model=UserResponse)
async def user_profile_update_handler(
    email: EmailStr = Form(...),
    picture: UploadFile = File(None),
    first_name: str = Form(..., alias="firstName", validation_alias="firstName"),
    last_name: str = Form(..., alias="lastName", validation_alias="lastName"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    user = await services.user_service.update_user_profile(
        token.user_id,
        email,
        picture,
        first_name,
        last_name,
    )

    if not user:
        raise NotFoundError(msg="User not found")

    return UserResponse.convert(user)


@router.post("/user/password/change", name="change-user-password")
async def change_user_password(
    passwords: ChangePasswordRequest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.user_service.change_password(
        old_password=passwords.old_password,
        new_password=passwords.new_password,
        user_id=token.user_id,
    )
    return Response(status_code=200)


@router.get("/user/profile", response_model=UserResponse)
async def user_profile_handler(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    user = await services.user_service.get_user_profile(
        token.user_id,
    )

    return UserResponse.convert(user)
