from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

    model_config = ConfigDict(from_attributes=True)
