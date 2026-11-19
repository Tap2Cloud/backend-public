from pydantic import BaseModel, ConfigDict, model_validator

from t2c_backend.models import Role


class RoleBase(BaseModel):
    id: int
    name: str
    permissions: str

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def permission_value_to_string(cls, data):
        # The bitmask can exceed JavaScript's safe integer range, so it is sent as a decimal
        # string. The stored value arrives as int/Decimal (Numeric column) or already as a string.
        return {**data, "permissions": str(int(data.get("permissions")))}

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


class PermissionResponse(BaseModel):
    name: str
    bit: int
    value: str
    requires: list[str]
    default: bool
