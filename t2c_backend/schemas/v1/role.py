from pydantic import BaseModel, ConfigDict

from t2c_backend.models import Role


class RoleBase(BaseModel):
    id: int
    name: str
    permissions: int

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(roles: list[Role]) -> list["RoleBase"]:
        return [RoleBase.convert_(role) for role in roles]

    @staticmethod
    def convert_(role: Role) -> "RoleBase":
        return RoleBase(
            id=role.id,
            name=role.name,
            permissions=role.permissions,
        )


class RoleCreate(BaseModel):
    name: str
    permissions: list[str]

    model_config = ConfigDict(from_attributes=True)
