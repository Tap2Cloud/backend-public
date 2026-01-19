from pydantic import BaseModel, Field


class Health(BaseModel):
    version: str = Field(..., examples=["1.0.0"])
    status: str = Field(..., examples=["OK"])
