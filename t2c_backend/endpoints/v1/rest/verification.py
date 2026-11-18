from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.user import (
    EmailVerificationCodeRequest,
    EmailVerificationCodeVerifyRequest,
    ForgotPasswordCodeRequest,
    ForgotPasswordCodeVerifyRequest,
    ForgotPasswordCodeVerifyResponse,
)
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer, get_frontend_url

router = APIRouter()


@router.post(
    "/email-verification/code/generate",
    operation_id="generate email verification code",
    status_code=200,
)
async def generate_email_verification_code(
    request: Request,
    data: EmailVerificationCodeRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    frontend_url = get_frontend_url(request)
    await services.user_email_token_service.resend_verification_code(
        str(data.email) if data.email else None, data.token, frontend_url
    )


@router.post(
    "/email-verification/code/auth/verify",
    operation_id="verify email code",
    status_code=200,
)
async def verify_email_code(
    data: EmailVerificationCodeVerifyRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    await services.user_email_token_service.verify_email_code(data.token, data.code)


@router.post(
    "/forgot-password/code/generate",
    operation_id="generate forgot password code",
    status_code=200,
)
async def generate_forgot_password_code(
    data: ForgotPasswordCodeRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    await services.user_email_token_service.send_forgot_password_code(str(data.email))


@router.post(
    "/forgot-password/code/auth/verify",
    operation_id="verify forgot password code",
    response_model=ForgotPasswordCodeVerifyResponse,
    status_code=200,
)
async def verify_forgot_password_code(
    data: ForgotPasswordCodeVerifyRequest,
    services: DictContainer = Depends(get_services),
) -> ForgotPasswordCodeVerifyResponse:
    reset_token = await services.user_email_token_service.verify_forgot_password_code(
        str(data.email), data.code
    )
    return ForgotPasswordCodeVerifyResponse(resetToken=reset_token)
