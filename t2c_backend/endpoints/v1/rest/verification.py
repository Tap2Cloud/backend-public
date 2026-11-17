from fastapi import APIRouter, Depends, Request, Response

from t2c_backend.clients.celery_app.tasks import forgot_password_mail
from t2c_backend.schemas.v1.user import (
    EmailVerificationCodeRequest,
    EmailVerificationCodeVerifyRequest,
)
from t2c_backend.services import get_services
from t2c_backend.utils.enums import TokenType
from t2c_backend.utils.errors import BadRequestError
from t2c_backend.utils.misc import DictContainer, get_frontend_url

router = APIRouter()


@router.post(
    "/email-verification/code/generate",
    name="generate-email-code",
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
    name="verify-email-code",
    operation_id="verify email code",
    status_code=200,
)
async def verify_email_code(
    data: EmailVerificationCodeVerifyRequest,
    services: DictContainer = Depends(get_services),
) -> None:
    await services.user_email_token_service.verify_email_code(data.token, data.code)


@router.post(
    "/forgot-password/token/generate",
    name="generate-forgot-password-email-token",
    status_code=200,
)
async def generate_forgot_password_email_token(
    email: str,
    services: DictContainer = Depends(get_services),
) -> None:
    user = await services.user_service.repository.get_one_or_none(email=email)

    if not user:
        raise BadRequestError("Please enter valid email")

    user_email_token = await services.user_email_token_service.create_token(
        user.id,
        TokenType.ForgotPasswordToken,
    )
    token_with_link = services.authentication.create_link_for_forgot_password_email_verification(
        user_email_token.user_token,
    )
    forgot_password_mail.delay(user.email, token_with_link)


@router.head("/forgot-password/token/verify", name="verify-forgot-password-email-token")
async def verify_forgot_password_email(
    verification_token: str,
    services: DictContainer = Depends(get_services),
):
    # Verify the forgot password token
    response = await services.user_email_token_service.verify_forgot_password_token(
        verification_token,
    )

    # Map response strings to corresponding status codes
    status_map = {
        "invalid token": 401,  # Unauthorized
        "already verified": 409,  # Conflict
        "time expired": 400,  # Bad Request
    }

    # Return appropriate status code or success if the token is valid
    return Response(status_code=status_map.get(response, 200))
