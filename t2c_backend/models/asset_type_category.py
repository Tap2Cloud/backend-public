from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
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
from t2c_backend.utils.enums import InputType

from .user import User

if TYPE_CHECKING:
    from .asset_type import AssetTypeField


class AssetTypeCategoryGroup(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "asset_type_category_group"

    name: Mapped[str] = mapped_column(Text())
    order: Mapped[int] = mapped_column(Numeric())


class AssetTypeCategory(
    BigIntPrimaryKey,
    CommonTableAttributes,
    AdvancedDeclarativeBase,
    AuditColumns,
):
    __tablename__ = "asset_type_categories"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "user_id",
            name="_asset_type_category_name_unique",
        ),
    )

    name: Mapped[str] = mapped_column(Text(), nullable=False)
    has_typeplates: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship("User")
    fields: Mapped[list["AssetTypeCategoryField"]] = relationship(
        "AssetTypeCategoryField",
        back_populates="asset_type_category",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )
    asset_type = relationship(
        "AssetType",
        back_populates="asset_type_category",
        uselist=True,
    )


class AssetTypeCategoryField(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "asset_type_category_fields"
    __table_args__ = (
        UniqueConstraint(
            "asset_type_category_id",
            "field_name",
            name="_unique_field_name_per_category",
        ),
        UniqueConstraint(
            "asset_type_category_id",
            "field_order",
            name="_unique_field_order_per_category",
        ),
    )
    field_type: Mapped[InputType] = mapped_column(Enum(InputType), nullable=False)

    field_name: Mapped[str] = mapped_column(Text(), nullable=False)
    field_place_holder: Mapped[str] = mapped_column(Text(), nullable=True)
    field_display_name: Mapped[str] = mapped_column(Text(), nullable=False)
    field_is_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    field_order: Mapped[int] = mapped_column(Numeric(), nullable=False)

    asset_type_category_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_categories.id", ondelete="CASCADE"),
    )

    asset_type_category_group_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_category_group.id", ondelete="CASCADE"),
    )

    asset_type_category_group: Mapped["AssetTypeCategoryGroup"] = relationship(
        "AssetTypeCategoryGroup",
    )

    asset_type_category: Mapped["AssetTypeCategory"] = relationship(
        "AssetTypeCategory",
        back_populates="fields",
    )
    options: Mapped[list["AssetTypeCategoryFieldOption"]] = relationship(
        back_populates="field",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
        order_by="AssetTypeCategoryFieldOption.id",
    )
    fields: Mapped[list["AssetTypeField"]] = relationship(
        "AssetTypeField",
        back_populates="asset_type_category_field",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )


class AssetTypeCategoryFieldOption(
    BigIntPrimaryKey,
    CommonTableAttributes,
    AdvancedDeclarativeBase,
):
    __tablename__ = "asset_type_category_field_options"
    __table_args__ = (
        UniqueConstraint(
            "option_id",
            "asset_field_type_category_field_id",
            name="_asset_field_type_category_field_option_unique",
        ),
    )

    option_id: Mapped[str] = mapped_column(Text(), nullable=False)
    option_label: Mapped[str] = mapped_column(Text(), nullable=False)
    asset_field_type_category_field_id: Mapped[int] = mapped_column(
        ForeignKey("asset_type_category_fields.id", ondelete="CASCADE"),
    )

    field: Mapped[list["AssetTypeCategoryField"]] = relationship(back_populates="options")
