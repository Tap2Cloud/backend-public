from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import AdvancedDeclarativeBase, BigIntPrimaryKey, CommonTableAttributes
from t2c_backend.utils.enums import ServiceTypes


class Service(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "services"
    contact: Mapped[str] = mapped_column(Text(), nullable=True)
    expire_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    service_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    web: Mapped[str] = mapped_column(Text(), nullable=True)
    email: Mapped[str] = mapped_column(Text(), nullable=True)
    service_type: Mapped[ServiceTypes] = mapped_column(Enum(ServiceTypes), nullable=False)

    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"))

    asset = relationship("Asset")
