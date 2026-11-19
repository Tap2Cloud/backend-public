from sqlalchemy import func

from t2c_backend.core.permissions import (
    DEFAULT_PERMISSIONS,
    PERMISSION_DEPENDENCIES,
    Permissions,
)
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Role
from t2c_backend.schemas.v1.role import RoleCreate
from t2c_backend.utils.enums import Role as RoleEnum
from t2c_backend.utils.errors import AlreadyExistsError, BadRequestError
from t2c_backend.utils.misc import escape_like, normalize_name


class RoleService:
    _model = Role

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def get_roles_by_organisation_id(
        self,
        organization_id: int,
    ):
        return await self.repository.list(organization_id=organization_id)

    async def create_role_by_organisation_id(self, organization_id: int, role_data: RoleCreate):
        name = normalize_name(role_data.name)
        if not name:
            raise BadRequestError(msg="Role name is required.")

        reserved_names = {role.name for role in RoleEnum.__members__.values()}
        if name.lower() in reserved_names:
            raise BadRequestError(msg=f"Role name '{name}' is reserved.")

        selected_permissions = set(role_data.permissions)
        invalid_permissions = selected_permissions - Permissions.VALID_FLAGS.keys()
        if invalid_permissions:
            raise BadRequestError(
                msg=f"Invalid permissions: {', '.join(sorted(invalid_permissions))}."
            )

        missing_permissions = [
            f"{permission} requires {', '.join(missing)}"
            for permission in sorted(selected_permissions)
            if (
                missing := [
                    required
                    for required in PERMISSION_DEPENDENCIES.get(permission, [])
                    if required not in selected_permissions
                ]
            )
        ]
        if missing_permissions:
            raise BadRequestError(
                msg=f"Missing required permissions: {'; '.join(missing_permissions)}."
            )

        selected_permissions |= DEFAULT_PERMISSIONS

        await self.repository.lock_values(
            name=func.lower(name),
            organization_id=organization_id,
        )

        is_role_exists = await self.repository.exists(
            name__ilike=escape_like(name),
            organization_id=organization_id,
        )
        if is_role_exists:
            raise AlreadyExistsError(msg="Role with this name already exists.")

        return await self.repository.save(
            Role(
                organization_id=organization_id,
                name=name,
                permissions=Permissions(**dict.fromkeys(selected_permissions, True)).value,
            ),
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(RoleService(app, session), session.info["session_id"])
