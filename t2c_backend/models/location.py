from sqlalchemy import (
    ForeignKey,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import AdvancedDeclarativeBase, BigIntPrimaryKey, CommonTableAttributes


class Location(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "locations"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(Text())
    street: Mapped[str] = mapped_column(Text(), nullable=True)
    postcode: Mapped[str] = mapped_column(Text(), nullable=True)
    city: Mapped[str] = mapped_column(Text())
    country: Mapped[str] = mapped_column(Text())
    region: Mapped[str] = mapped_column(Text(), nullable=True)

    tel_number: Mapped[str] = mapped_column(Text(), nullable=True)
    mobile_number: Mapped[str] = mapped_column(Text())
    fax_number: Mapped[str] = mapped_column(Text(), nullable=True)
    email: Mapped[str] = mapped_column(Text())

    organization = relationship("Organization")
    asset = relationship(
        "Asset",
        back_populates="location",
        cascade="all, delete",
        passive_deletes=True,
    )
    user = relationship(
        "User",
        back_populates="location",
        cascade="all, delete",
        passive_deletes=True,
    )
