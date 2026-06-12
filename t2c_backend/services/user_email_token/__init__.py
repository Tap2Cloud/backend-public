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


def setup(app, session, *args, **kwargs):
    return app.add_service(UserEmailTokenService(app, session), session.info["session_id"])
