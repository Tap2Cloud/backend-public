import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
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

from .asset_type_category import (
    AssetTypeCategory,
    AssetTypeCategoryField,
    AssetTypeCategoryFieldOption,
)
from .location import Location
from .user import User


class AssetType(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "asset_types"

    name: Mapped[str] = mapped_column(Text(), nullable=False)
    video_links: Mapped[str] = mapped_column(Text(), nullable=True)
    video_title: Mapped[str] = mapped_column(Text(), nullable=True)
    web_link: Mapped[str] = mapped_column(Text(), nullable=True)
    web_link_title: Mapped[str] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(), default=0, nullable=True)
    manufacturer: Mapped[str] = mapped_column(Text(), nullable=True)
    asset_type_category_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_categories.id", ondelete="CASCADE"),
    )
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    # user_id is kept only as a "created by" acknowledgement; it is never used for
    # scoping/ownership. Ownership is derived from location_id (user -> location -> org).
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    location: Mapped["Location"] = relationship("Location")
    user: Mapped["User"] = relationship("User")
    asset_type_category: Mapped["AssetTypeCategory"] = relationship("AssetTypeCategory")
    fields: Mapped[list["AssetTypeField"]] = relationship(
        "AssetTypeField",
        back_populates="asset_type",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    typeplate = relationship(
        "Typeplate",
        back_populates="asset_type",
        uselist=False,
        lazy="selectin",
    )
    documents: Mapped[list["AssetTypeDocument"]] = relationship(
        "AssetTypeDocument",
        back_populates="asset_type",
        uselist=True,
    )


class AssetTypeDocument(CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "asset_types_documents"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "asset_type_id",
            name="_name_asset_type_asset_type_id_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    content_type: Mapped[str] = mapped_column(Text(), nullable=False)

    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="CASCADE"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    asset_type = relationship("AssetType")
    location: Mapped["Location"] = relationship("Location")
    user: Mapped["User"] = relationship("User")


class AssetTypeField(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "asset_type_fields"

    field_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_category_fields.id", ondelete="CASCADE"),
    )
    response_value: Mapped[str] = mapped_column(Text(), nullable=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="CASCADE"))

    asset_type: Mapped["AssetType"] = relationship("AssetType", back_populates="fields")
    asset_type_field_options: Mapped[list["AssetTypeFieldOptions"]] = relationship(
        back_populates="field",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )
    asset_type_category_field: Mapped["AssetTypeCategoryField"] = relationship(
        "AssetTypeCategoryField", back_populates="fields"
    )


class AssetTypeFieldOptions(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "asset_type_field_options"

    option_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_category_field_options.id", ondelete="CASCADE")
    )
    asset_type_field_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_fields.id", ondelete="CASCADE"),
    )

    field: Mapped["AssetTypeField"] = relationship(back_populates="asset_type_field_options")

    asset_type_category_field_options: Mapped["AssetTypeCategoryFieldOption"] = relationship(
        "AssetTypeCategoryFieldOption"
    )
