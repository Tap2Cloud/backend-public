from sqlalchemy import (
    ForeignKey,
    Text,
    func,
    select,
)
from sqlalchemy.orm import (
    Mapped,
    column_property,
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
from t2c_backend.schemas.v1.image import Image


class Organization(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "organizations"

    taxonomy_id: Mapped[int] = mapped_column(ForeignKey("taxonomies.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(Text())
    number: Mapped[str] = mapped_column(Text())
    email: Mapped[str] = mapped_column(Text())
    logo: Mapped["Image"] = mapped_column(ImageType(), nullable=True)
    taxonomy = relationship("Taxonomy")
    organization_rented_assets = relationship(
        "OrganizationRentedAsset", back_populates="organization"
    )

    location = relationship(
        "Location",
        back_populates="organization",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return self.name


def add_location_count(organization_model: type[Organization]):
    from .location import Location

    organization_model.location_count = column_property(
        select(func.count(Location.id))
        .where(Location.organization_id == Organization.id)
        .correlate(organization_model)
        .scalar_subquery()
    )


def add_user_count(organization_model: type[Organization]):
    from .location import Location
    from .user import User

    organization_model.user_count = column_property(
        select(func.count(User.id))
        .join(Location, User.location_id == Location.id)
        .where(Location.organization_id == Organization.id)
        .correlate(Organization)
        .scalar_subquery()
    )


def add_role_count(organization_model: type[Organization]) -> None:
    from .role import Role

    organization_model.role_count = column_property(
        select(func.count(Role.id))
        .where(Role.organization_id == organization_model.id)
        .correlate(organization_model)
        .scalar_subquery()
    )
