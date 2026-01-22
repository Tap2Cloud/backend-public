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
from t2c_backend.models.documents import Document
from t2c_backend.schemas.v1.image import Image

if TYPE_CHECKING:
    from t2c_backend.models import AssetType


class Typeplate(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "typeplates"

    test_results: Mapped[str] = mapped_column(Text(), nullable=True)
    eu_id: Mapped[str] = mapped_column(Text(), nullable=True)
    eu_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=True
    )
    carbon_footprint_label: Mapped[str] = mapped_column(Text(), nullable=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="CASCADE"))

    asset_type: Mapped["AssetType"] = relationship("AssetType")
    eu_file: Mapped["Document"] = relationship("Document")
    typeplate_documents = relationship(
        "TypeplateDocument",
        back_populates="typeplate",
        uselist=True,
    )
    typeplate_images: Mapped[list["TypelateImageMapping"]] = relationship(
        "TypelateImageMapping",
        back_populates="typeplate",
        uselist=True,
    )


class TypeplateDocument(
    BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns
):
    __tablename__ = "typeplate_documents"

    typeplate_id: Mapped[int] = mapped_column(ForeignKey("typeplates.id", ondelete="CASCADE"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))

    typeplate: Mapped["Typeplate"] = relationship("Typeplate")
    document: Mapped["Document"] = relationship("Document")


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

    typeplate: Mapped["Typeplate"] = relationship("Typeplate")
    typeplate_image: Mapped["TypeplateImage"] = relationship("TypeplateImage")
