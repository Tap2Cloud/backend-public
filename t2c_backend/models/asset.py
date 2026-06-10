from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Text,
    UniqueConstraint,
    desc,
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
from t2c_backend.models.audit import Audit
from t2c_backend.models.service import Service
from t2c_backend.utils.enums import AssetStatus


class Asset(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "location_id",
            name="_unique_device_id_location_id",
        ),
    )

    pass_id: Mapped[str] = mapped_column(Text())
    device_id: Mapped[str] = mapped_column(Text())
    manufacturing_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), nullable=False)
    serial_no: Mapped[str] = mapped_column(Text(), nullable=True)
    economic_operator: Mapped[str] = mapped_column(Text(), nullable=True)

    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="CASCADE"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    # todo holder related code left

    location = relationship("Location")
    asset_type = relationship(
        "AssetType",
        cascade="all, delete",
        passive_deletes=True,
    )

    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="asset",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )

    audit: Mapped[list["Audit"]] = relationship("Audit", order_by=desc(Audit.id))
