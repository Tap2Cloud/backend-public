from fastapi import APIRouter, Depends, Response
from services import get_services

from t2c_backend.utils.enums import TokenType
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
