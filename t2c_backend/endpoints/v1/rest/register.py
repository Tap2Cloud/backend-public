from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.user import UserRegisterRequest
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer, get_frontend_url

router = APIRouter()


@router.post("/register", name="register", status_code=200)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    frontend_url = get_frontend_url(request)
    await services.user_service.register_user(
        str(user_data.email),
        user_data.password,
        user_data.first_name,
        user_data.last_name,
        frontend_url,
        user_data.language,
    )
