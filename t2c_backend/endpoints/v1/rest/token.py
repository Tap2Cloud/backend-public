from fastapi import APIRouter, Depends, Request

from t2c_backend.core.security import JWTAPIRefreshTokenBearer
from t2c_backend.schemas.v1.token import (
    AccessToken,
    RefreshToken,
    RefreshTokenResponse,
)
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get("/token/refresh", name="token", response_model=RefreshTokenResponse, status_code=200)
async def token_refresh(
    request: Request,
    token: RefreshToken = Depends(JWTAPIRefreshTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    db_user = await services.user_service.repository.get_one_or_none(id=token.user_id)
    return RefreshTokenResponse(
        access_token=str(AccessToken.for_user(db_user, request.app.clients.token_backend))
    )
