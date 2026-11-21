from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.user import UserRegisterRequest, VerificationTokenResponse
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer, get_frontend_url

router = APIRouter()


@router.post("/register", name="register", status_code=200)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    services: DictContainer = Depends(get_services),
) -> VerificationTokenResponse:
    frontend_url = get_frontend_url(request)
    user = await services.user_service.register_user(
        str(user_data.email),
        user_data.password,
        user_data.first_name,
        user_data.last_name,
        frontend_url,
        user_data.language,
    )
    # lets the frontend open /verify?token=… right away; the emailed code is still required
    token = await services.user_email_token_service.get_verification_token(user)
    return VerificationTokenResponse(token=token)
