from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.token import AccessToken, RefreshToken, TokenResponse
from t2c_backend.schemas.v1.user import UserRegisterRequest
from t2c_backend.services import get_services
from t2c_backend.utils.enums import TokenType
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/register", name="register", response_model=TokenResponse, status_code=200)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    services: DictContainer = Depends(get_services),
):
    user = await services.user_service.register_user(
        str(user_data.email),
        user_data.password,
        user_data.first_name,
        user_data.last_name,
    )
    await services.user_email_token_service.create_token(
        user.id,
        TokenType.EmailVerificationToken,
    )
    return TokenResponse(
        access_token=str(AccessToken.for_user(user, request.app.clients.token_backend)),
        refresh_token=str(RefreshToken.for_user(user, request.app.clients.token_backend)),
    )
