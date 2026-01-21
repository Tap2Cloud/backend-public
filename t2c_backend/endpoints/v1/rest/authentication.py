from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.token import AccessToken, RefreshToken
from t2c_backend.schemas.v1.user import UserLogin, UserLoginResponse
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/login", name="login", status_code=200)
async def login(request: Request, user: UserLogin, services: DictContainer = Depends(get_services)):
    db_user = await services.user_service.login(
        email=str(user.email),
        password=user.password,
    )

    return UserLoginResponse(
        access_token=str(AccessToken.for_user(db_user, request.app.clients.token_backend)),
        refresh_token=str(RefreshToken.for_user(db_user, request.app.clients.token_backend)),
    )
