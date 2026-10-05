from fastapi import APIRouter, Depends, Response
from services import get_services

from t2c_backend.clients.celery_app.tasks import forgot_password_mail, verification_mail
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.utils.enums import TokenType
from t2c_backend.utils.errors import BadRequestError
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/email-verification/token/verify", name="verify-email-token")
async def verify_email(
    user_token: str,
    services: DictContainer = Depends(get_services),
):
    # Fetch the token details
    user_email_token = await services.user_email_token_service.find_by_token(
        user_token,
    )

    # Check if the token exists and is valid
    if not user_email_token or user_email_token.type == TokenType.ForgotPasswordToken:
        return Response(status_code=401)

    # Check if the email is already verified or the token has been used
    if user_email_token.user.is_email_verified or user_email_token.is_used:
        return Response(status_code=409)  # Conflict: Already verified or token used

    # Attempt to verify the token
    if not await services.user_email_token_service.verify_email_token(
        user_email_token,
    ):
        return Response(status_code=400)  # Bad Request: Invalid credentials

    # Successfully verified
    return Response(status_code=200)


@router.post("/email-verification/token/generate", name="generate-email-token", status_code=200)
async def generate_email_verification_token(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
) -> None:
    user_email_token = await services.user_email_token_service.create_token(
        token.user_id,
        TokenType.EmailVerificationToken,
    )
    token_with_link = services.authentication.create_link_for_user_email_verification(
        user_email_token.user_token,
    )
    verification_mail.delay(user_email_token.user.email, token_with_link)


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
