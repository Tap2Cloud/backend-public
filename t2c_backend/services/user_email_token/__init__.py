import datetime
from uuid import uuid4

from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import UserEmailToken
from t2c_backend.utils.enums import TokenType


class UserEmailTokenService:
    _model = UserEmailToken

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def create_token(self, user_id: int, token_type: TokenType) -> UserEmailToken:
        """Creates and saves a new email token."""
        user_email_token = UserEmailToken(user_id=user_id, user_token=uuid4().hex, type=token_type)
        return await self.repository.save(user_email_token, refresh=True)

    async def find_by_token(self, token: str) -> UserEmailToken | None:
        """Finds a user token by its string value."""
        return await self.repository.get_one_or_none(user_token=token, is_used__is_not=True)

    async def verify_email_token(self, user_email_token: UserEmailToken) -> bool:
        """Verifies if the email token is valid and activates the user account."""
        if self._is_token_expired(user_email_token):
            return False

        # If token is not expired, verify the associated user and commit changes.
        user = user_email_token.user
        user.is_active = True
        user.is_email_verified = True

        user_email_token.is_used = True

        await self.app.services.user_service.repository.save(user)
        await self.repository.save(user_email_token)
        return True

    def _is_token_expired(
        self,
        user_email_token: UserEmailToken,
        is_forgot_password: bool = False,
    ) -> bool:
        """Helper method to check if the token has expired."""
        expiry_hours = (
            self.app.config.USER_FORGOT_PASSWORD_TOKEN_EXPIRY_HOURS
            if is_forgot_password
            else self.app.config.USER_EMAIL_TOKEN_EXPIRY_HOURS
        )

        difference = datetime.datetime.now(datetime.UTC) - user_email_token.time
        hours = difference.total_seconds() / 3600
        return hours > expiry_hours


def setup(app, session, *args, **kwargs):
    return app.add_service(UserEmailTokenService(app, session), session.info["session_id"])
