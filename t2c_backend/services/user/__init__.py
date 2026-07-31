from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import case, func, or_, select, union_all
from sqlalchemy.orm import joinedload

from t2c_backend.core.pagination import CustomParams
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    Location,
    Organization,
    Role,
    User,
    UserRole,
)
from t2c_backend.models.product_pass_type import ProductPassType
from t2c_backend.models.user import UserInviteRole
from t2c_backend.schemas.v1.image import Image
from t2c_backend.schemas.v1.user import OrganizationUser, OrganizationUsersCustomPage, UserCount
from t2c_backend.utils.enums import UserStatus
from t2c_backend.utils.errors import (
    AlreadyExistsError,
    BadRequestError,
    NotFoundError,
    UnAuthorizedError,
)


class UserService:
    _model = User

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.user_invite_role_repository = BaseRepository(app, session, UserInviteRole)
        self.user_role_repository = BaseRepository(app, session, UserRole)

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

    async def get_user_profile(self, user_id: int) -> User:
        user = await self.repository.get(
            user_id,
            options=[
                joinedload(User.location)
                .joinedload(Location.organization)
                .joinedload(Organization.product_pass_type),
                joinedload(User.roles),
            ],
        )

        if not user:
            raise NotFoundError("User not found")

        return user

    async def delete_user(self, user_id: int, organization_id: int, cascade_org: bool) -> bool:
        db_user = await self.repository.get_one_or_none(
            id=user_id, options=[joinedload(User.location)]
        )

        if (
            not db_user
            or not db_user.location
            or db_user.location.organization_id != organization_id
        ):
            raise NotFoundError("User not found")

        other_users_exist = await self.repository.session.scalar(
            select(
                select(User.id)
                .join(Location, User.location_id == Location.id)
                .where(User.id != user_id, Location.organization_id == organization_id)
                .exists()
            )
        )

        if other_users_exist:
            await self.repository.delete(id=db_user.id)
        elif cascade_org:
            await self.app.services.organization_service.delete_organization(
                organization_id=organization_id
            )
        else:
            raise BadRequestError(msg="Unable to delete this user")

        return True

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

    async def update_user_profile(
        self,
        user_id,
        picture,
        first_name,
        last_name,
    ):
        user = await self.get_user_profile(user_id)

        update_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "profile_avatar": await Image.from_file(picture) if picture else None,
        }

        for field, value in update_fields.items():
            if field == "first_name" and value == "" or field == "last_name" and value == "":
                raise BadRequestError(msg="First name or last name required")

            setattr(user, field, value)

        return await self.repository.save(user)

    async def change_password(self, old_password: str, new_password: str, user_id: int) -> bool:
        db_user = await self.repository.get_one_or_none(id=user_id)

        is_valid_password = (
            self.app.services.authentication.verify_hash(old_password, db_user.salt)
            == db_user.hashed_password
        )
        if not is_valid_password:
            raise UnAuthorizedError(msg="Incorrect old password")

        salt, hashed_password = self.app.services.authentication.generate_encoded_password(
            new_password
        )
        db_user.salt = salt
        db_user.hashed_password = hashed_password

        await self.repository.save(db_user)

        return True

    async def organization_user_handler(
        self,
        query: str | None,
        roles: list[str],
        status: UserStatus | None,
        page: int,
        page_size: int,
        organization_id: int,
    ):
        if not organization_id:
            raise NotFoundError(msg="Organization not found")

        user_select = (
            select(
                self._model.id,
                self._model.first_name,
                self._model.last_name,
                self._model.email,
                self._model.created_at,
                case(
                    (self._model.is_active.is_(True), UserStatus.ACTIVE),
                    (self._model.is_active.is_(False), UserStatus.BANNED),
                ).label("status"),
                Location.id.label("location_id"),
                Location.city.label("location_city"),
                Location.country.label("location_country"),
                Organization.id.label("organization_id"),
                Organization.name.label("organization_name"),
                Organization.number.label("organization_number"),
                Organization.created_at.label("organization_created_at"),
                func.array_agg(
                    func.jsonb_build_object(
                        "id",
                        ProductPassType.id,
                        "name",
                        ProductPassType.name,
                        "display_name",
                        ProductPassType.display_name,
                    )
                ).label("organization_product_pass_type"),
                func.array_agg(
                    func.jsonb_build_object(
                        "id",
                        Role.id,
                        "name",
                        Role.name,
                        "permissions",
                        Role.permissions,
                    )
                ).label("roles"),
            )
            .join(self._model.location)
            .join(Location.organization)
            .where(Location.organization_id == organization_id)
            .join(UserRole, UserRole.user_id == self._model.id)
            .join(Role, Role.id == UserRole.role_id)
            .join(ProductPassType, ProductPassType.id == Organization.product_pass_type_id)
            .group_by(User.id, Location.id, Organization.id)
        )

        if query:
            user_select = user_select.filter(
                or_(
                    *BaseRepository.parse_filters(self._model, first_name__ilike=f"%{query}%"),
                    *BaseRepository.parse_filters(self._model, last_name__ilike=f"%{query}%"),
                    *BaseRepository.parse_filters(self._model, email__ilike=f"%{query}%"),
                )
            )

        if roles:
            user_select = user_select.where(
                User.id.in_(
                    select(UserRole.user_id)
                    .join(Role, Role.id == UserRole.role_id)
                    .where(Role.name.in_(roles))
                )
            )

        final_query = union_all(user_select)

        if status == UserStatus.ACTIVE:
            final_query = user_select.filter(
                *BaseRepository.parse_filters(self._model, is_active=True)
            )

        if status == UserStatus.BANNED:
            final_query = user_select.filter(
                *BaseRepository.parse_filters(self._model, is_active=False)
            )

        user_subquery = user_select.subquery()

        # Apply conditional counts
        user_count_query = select(
            func.count(case((user_subquery.c.status == UserStatus.ACTIVE, 1))).label("active"),
            func.count(case((user_subquery.c.status == UserStatus.BANNED, 1))).label("banned"),
        ).select_from(user_subquery)

        user_count = (await self.repository.session.execute(user_count_query)).fetchone()

        return await apaginate(
            self.repository.session,
            final_query,
            params=CustomParams(page=page, pageSize=page_size),
            config=Config(page_cls=OrganizationUsersCustomPage),
            transformer=lambda users: [
                OrganizationUser.convert(
                    {
                        **user._asdict(),
                        "location": Location(
                            id=user.location_id,
                            city=user.location_city,
                            country=user.location_country,
                        ),
                        "organization": Organization(
                            id=user.organization_id,
                            name=user.organization_name,
                            number=user.organization_number,
                            created_at=user.organization_created_at,
                            product_pass_type=ProductPassType(
                                id=user.organization_product_pass_type[0].get("id"),
                                name=user.organization_product_pass_type[0].get("name"),
                                display_name=user.organization_product_pass_type[0].get(
                                    "display_name"
                                ),
                            ),
                        ),
                    }
                )
                for user in users
            ],
            additional_data={
                "extra": UserCount(
                    active=user_count.active,
                    banned=user_count.banned,
                ),
            },
            unique=False,
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(UserService(app, session), session.info["session_id"])
