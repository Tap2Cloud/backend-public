from pydantic import BaseModel, ConfigDict, EmailStr, Field

from t2c_backend.schemas.v1.token import TokenResponse


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserLogin(UserBase): ...


class UserLoginResponse(TokenResponse): ...
