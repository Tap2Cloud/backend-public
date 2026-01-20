from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    Sequence,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_mixin,
    declared_attr,
    mapped_column,
    validates,
)


class AdvancedDeclarativeBase(DeclarativeBase):
    pass


@declarative_mixin
class BigIntPrimaryKey:
    """BigInt Primary Key Field Mixin."""

    # noinspection PyNestedDecorators
    @declared_attr
    @classmethod
    def id(cls) -> Mapped[int]:
        """BigInt Primary key column."""
        return mapped_column(
            BigInteger,
            Sequence(f"{cls.__tablename__}_id_seq", optional=False),
            primary_key=True,
            sort_order=-1,
        )


@declarative_mixin
class AuditColumns:
    """Created/Updated At Fields Mixin."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    """Date/time of instance creation."""
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    """Date/time of instance last update."""

    @validates("created_at", "updated_at")
    def validate_tz_info(self, _: str, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value


class BasicAttributes:
    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dict[str, Any]: A dict representation of the model
        """
        exclude = {"sa_orm_sentinel", "_sentinel"}.union(self._sa_instance_state.unloaded).union(
            exclude or [],
        )
        return {
            field: getattr(self, field)
            for field in self.__mapper__.columns.keys()  # noqa: SIM118
            if field not in exclude
        }


class CommonTableAttributes(BasicAttributes):
    __table__ = ...
