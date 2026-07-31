from sqlalchemy import Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import AdvancedDeclarativeBase, BigIntPrimaryKey, CommonTableAttributes


class ProductPassType(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "product_pass_types"

    name: Mapped[str] = mapped_column(Text())
    display_name: Mapped[str] = mapped_column(Text())

    organization = relationship(
        "Organization",
        back_populates="product_pass_type",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return self.name
