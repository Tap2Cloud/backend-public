import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    ColumnElement,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    literal_column,
    text,
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

# Spelled as literal_column rather than as bound parameters so that the expression renders the
# same characters in an index definition as it does in a query. A bound backslash is escaped
# differently depending on what the server reports for standard_conforming_strings, and an index
# whose expression differs by one character from the query's is an index the query cannot use.
_WHITESPACE_RUN = literal_column(r"'\s+'")
_SINGLE_SPACE = literal_column("' '")
_GLOBAL = literal_column("'g'")

ASSET_TYPE_NAME_UNIQUE_INDEX = "uq_asset_type_name_per_category"


def normalized_asset_type_name(name: ColumnElement[str]) -> ColumnElement[str]:
    return func.lower(
        func.btrim(func.regexp_replace(name, _WHITESPACE_RUN, _SINGLE_SPACE, _GLOBAL))
    )


class AssetType(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "asset_types"

    __table_args__ = (
        Index(
            ASSET_TYPE_NAME_UNIQUE_INDEX,
            "asset_type_category_id",
            normalized_asset_type_name(text("name")),
            unique=True,
        ),
    )

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
    # ondelete=SET NULL so deleting the creator never removes location-owned data.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

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
    # created-by only; SET NULL so deleting the creator keeps location-owned documents.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

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
