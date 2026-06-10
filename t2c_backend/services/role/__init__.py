from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Role
from t2c_backend.schemas.v1.role import RoleCreate


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
        return await self.repository.save(
            Role(
                organization_id=organization_id,
                name=role_data.name,
            ),
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(RoleService(app, session), session.info["session_id"])
