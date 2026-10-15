import uuid

from pydantic import BaseModel, ConfigDict, Field

from t2c_backend.models import Document
from t2c_backend.utils.misc import datetime_to_epoch


class DocumentResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    status: str
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(fields: "Document") -> "DocumentResponse":
        return DocumentResponse(
            id=fields.id,
            name=fields.name,
            type=fields.type,
            status=fields.status,
            createdAt=datetime_to_epoch(fields.created_at),
        )
