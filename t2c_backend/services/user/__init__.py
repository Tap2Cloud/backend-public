from sqlalchemy import select

from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Location, Organization, Role, User, UserRole
from t2c_backend.utils.errors import AlreadyExistsError, UnAuthorizedError


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

    async def login(self, email: str, password: str) -> User:
        # Fetch user data from the repository
        db_user = await self.repository.get_one_or_none(email=email)

        if not db_user:
            raise UnAuthorizedError(msg="Not authenticated")

        # Verify the password
        is_valid_password = (
            self.app.services.authentication.verify_hash(password, db_user.salt)
            == db_user.hashed_password
        )
        if not is_valid_password:
            raise UnAuthorizedError(msg="Incorrect username or password")

        return db_user

    async def get_user_org_location_and_roles(self, user_id: int) -> dict:
        stmt = (
            select(
                User.id.label("user_id"),
                Location.id.label("location_id"),
                Organization.id.label("organization_id"),
                Role.id.label("role_id"),
                Role.name.label("role_name"),
                Role.permissions.label("role_permissions"),
            )
            .outerjoin(User.location)
            .outerjoin(Location.organization)
            .outerjoin(User.roles)
            .filter(User.id == user_id)
        )

        result = await self.repository.execute(stmt)
        rows = result.fetchall()

        return {
            "user_id": rows[0].user_id,
            "location_id": rows[0].location_id,
            "organization_id": rows[0].organization_id,
            "roles": [
                {
                    "id": row.role_id,
                    "name": row.role_name,
                    "permissions": row.role_permissions,
                }
                for row in rows
                if row.role_id is not None
            ],
        }


def setup(app, session, *args, **kwargs):
    return app.add_service(UserService(app, session), session.info["session_id"])
