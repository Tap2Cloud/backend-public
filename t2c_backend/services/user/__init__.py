from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import User, UserRole
from t2c_backend.utils.errors import AlreadyExistsError


class UserService:
    _model = User

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.user_role_repository = BaseRepository(app, session, UserRole)

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        is_user_exists = await self.repository.exists(email=email)

        if is_user_exists:
            raise AlreadyExistsError(msg="Email already registered")

        salt, hashed_password = self.app.services.authentication.generate_encoded_password(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            salt=salt,
            first_name=first_name,
            last_name=last_name,
            roles=[],
        )

        return await self.repository.save(user)


def setup(app, session, *args, **kwargs):
    return app.add_service(UserService(app, session), session.info["session_id"])
