import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import (
    AdvancedDeclarativeBase,
    AuditColumns,
    BigIntPrimaryKey,
    CommonTableAttributes,
)
from t2c_backend.core.db.types import ImageType
from t2c_backend.models.location import Location
from t2c_backend.models.user import User
from t2c_backend.schemas.v1.image import Image

if TYPE_CHECKING:
    from t2c_backend.models import AssetType


class Typeplate(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "typeplates"

    test_results: Mapped[str] = mapped_column(Text(), nullable=True)
    eu_id: Mapped[str] = mapped_column(Text(), nullable=True)
    carbon_footprint_label: Mapped[str] = mapped_column(Text(), nullable=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="CASCADE"))

    asset_type: Mapped["AssetType"] = relationship("AssetType")
    documents: Mapped[list["TypeplateDocument"]] = relationship(
        "TypeplateDocument",
        back_populates="typeplate",
        cascade="all, delete-orphan",
        uselist=True,
        lazy="selectin",
    )
    typeplate_images: Mapped[list["TypelateImageMapping"]] = relationship(
        "TypelateImageMapping",
        back_populates="typeplate",
        cascade="all, delete-orphan",
        uselist=True,
        lazy="selectin",
    )


class TypeplateDocument(
    BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns
):
    __tablename__ = "typeplate_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    content_type: Mapped[str] = mapped_column(Text(), nullable=False)

    typeplate_id: Mapped[int] = mapped_column(ForeignKey("typeplates.id", ondelete="CASCADE"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    # created-by only; SET NULL so deleting the creator keeps location-owned documents.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    typeplate: Mapped["Typeplate"] = relationship("Typeplate", back_populates="documents")
    location: Mapped["Location"] = relationship("Location")
    user: Mapped["User"] = relationship("User")


class TypeplateImage(CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "typeplate_images"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    image: Mapped["Image"] = mapped_column(ImageType(), nullable=True)


class TypelateImageMapping(
    BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns
):
    __tablename__ = "typelate_image_mapping"

    typeplate_id: Mapped[int] = mapped_column(ForeignKey("typeplates.id", ondelete="CASCADE"))
    typeplate_image_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("typeplate_images.id", ondelete="CASCADE")
    )

    typeplate: Mapped["Typeplate"] = relationship("Typeplate", back_populates="typeplate_images")
    typeplate_image: Mapped["TypeplateImage"] = relationship("TypeplateImage", lazy="selectin")
