from pydantic import BaseModel, ConfigDict, EmailStr, Field

from t2c_backend.core.pagination import CustomPage
from t2c_backend.models import User as UserModel
from t2c_backend.schemas.v1.location import Location, LocationBaseResponse
from t2c_backend.schemas.v1.role import RoleBase
from t2c_backend.schemas.v1.token import TokenResponse
from t2c_backend.utils.enums import Role as RoleEnum
from t2c_backend.utils.enums import UserStatus
from t2c_backend.utils.misc import get_full_name


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserLogin(UserBase): ...


class UserLoginResponse(TokenResponse): ...


class UserCount(BaseModel):
    active: int
    banned: int


class OrganizationUsersCustomPage(CustomPage):
    __qualname__ = "Page"

    extra: UserCount


class DisplayUser(BaseModel):
    id: int
    email: str
    profile_avatar: str | None = Field(..., alias="profileAvatar")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    full_name: str = Field(..., alias="fullName")
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(user: UserModel) -> "DisplayUser":
        return DisplayUser(
            id=user.id,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            fullName=user.get_full_name(),
            createdAt=int(user.created_at.timestamp()),
            profileAvatar=user.profile_avatar.get_string()
            if user.profile_avatar is not None
            else None,
        )


class UserResponse(DisplayUser):
    email_verified: bool = Field(..., alias="emailVerified")
    roles: list[RoleBase]
    location: Location | None
    profile_avatar: str | None = Field(..., alias="profileAvatar")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(user: UserModel) -> "UserResponse":
        return UserResponse(
            id=user.id,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            fullName=user.get_full_name(),
            emailVerified=user.is_email_verified,
            roles=RoleBase.convert(user.roles),
            createdAt=int(user.created_at.timestamp()),
            location=(
                Location.convert(user.location, user.location.organization)
                if user.location
                else None
            ),
            profileAvatar=user.profile_avatar.get_string()
            if user.profile_avatar is not None
            else None,
        )


class OrganizationUser(DisplayUser):
    roles: list[RoleBase]
    status: UserStatus
    location: LocationBaseResponse | None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(row) -> "OrganizationUser":
        return OrganizationUser(
            id=row.get("id"),
            email=row.get("email"),
            firstName=row.get("first_name"),
            lastName=row.get("last_name"),
            fullName=get_full_name(row.get("first_name"), row.get("last_name")),
            createdAt=int(row.get("created_at").timestamp()),
            location=LocationBaseResponse.convert(row.get("location"), row.get("organization")),
            roles=[
                RoleBase(
                    id=role.get("id"),
                    name=RoleEnum[role.get("name")].value,
                    permissions=role.get("permissions"),
                )
                for role in row.get("roles")
            ],
            status=row.get("status"),
            profileAvatar=row.get("profile_avatar").get_string()
            if row.get("profile_avatar") is not None
            else None,
        )


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., alias="newPassword")
