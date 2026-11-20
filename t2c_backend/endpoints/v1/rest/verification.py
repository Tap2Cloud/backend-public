from fastapi import APIRouter, Depends, Request

from t2c_backend.schemas.v1.token import AccessToken, RefreshToken
from t2c_backend.schemas.v1.user import (
    EmailVerificationCodeRequest,
    EmailVerificationCodeVerifyRequest,
    EmailVerificationTokenRequest,
    ForgotPasswordCodeRequest,
    ForgotPasswordCodeVerifyRequest,
    ForgotPasswordCodeVerifyResponse,
    UserLoginResponse,
    VerificationTokenResponse,
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
) -> VerificationTokenResponse:
    # returns the token so sign-in (unverified email) can open /verify?token=… right away
    frontend_url = get_frontend_url(request)
    token = await services.user_email_token_service.resend_verification_code(
        data.source, str(data.email) if data.email else None, data.token, frontend_url
    )
    return VerificationTokenResponse(token=token)


@router.post(
    "/email-verification/token/validate",
    operation_id="validate email verification token",
    status_code=200,
)
async def validate_email_verification_token(
    data: EmailVerificationTokenRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    await services.user_email_token_service.validate_verification_token(data.token)


@router.post(
    "/email-verification/code/auth/verify",
    operation_id="verify email code",
    status_code=200,
)
async def verify_email_code(
    request: Request,
    data: EmailVerificationCodeVerifyRequest,
    services: DictContainer = Depends(get_services),
) -> UserLoginResponse:
    user = await services.user_email_token_service.verify_email_code(data.token, data.code)
    # the code proves the inbox, so sign the user in instead of sending them to the login page
    token_backend = request.app.clients.token_backend
    return UserLoginResponse(
        access_token=str(AccessToken.for_user(user, token_backend)),
        refresh_token=str(RefreshToken.for_user(user, token_backend)),
    )


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
