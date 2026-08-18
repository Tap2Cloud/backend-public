import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import AdvancedDeclarativeBase, AuditColumns, CommonTableAttributes
from t2c_backend.utils.enums import DocumentStatus, DocumentType

if TYPE_CHECKING:
    from t2c_backend.models import Location, User


class Document(CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "documents"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "type",
            "location_id",
            name="_name_type_location_location_id_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=True)
    type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    content_type: Mapped[str] = mapped_column(Text(), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    # created-by only; SET NULL so deleting the creator keeps location-owned documents.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    location: Mapped["Location"] = relationship("Location")
    user: Mapped["User"] = relationship("User")
