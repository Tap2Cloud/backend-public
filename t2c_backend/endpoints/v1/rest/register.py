from fastapi import APIRouter, Depends

from t2c_backend.schemas.v1.user import UserRegisterRequest
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/register", name="register", status_code=200)
async def register(
    user_data: UserRegisterRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    await services.user_service.register_user(
        str(user_data.email),
        user_data.password,
        user_data.first_name,
        user_data.last_name,
        user_data.language,
    )
