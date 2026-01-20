from sqlalchemy import (
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from t2c_backend.core.db import AdvancedDeclarativeBase, BigIntPrimaryKey, CommonTableAttributes
from t2c_backend.models import user

from .organization import Organization


class Role(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "roles"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(Text(), nullable=True)
    permissions: Mapped[int] = mapped_column(Numeric(), default=0)

    organization: Mapped["Organization"] = relationship("Organization")
    users: Mapped[list["user.User"]] = relationship(
        "User",
        uselist=True,
        secondary="user_roles",
        back_populates="roles",
    )

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def convert(roles, **kwargs):
        return [Role(**rs.model_dump(), **kwargs) for rs in roles]


class UserRole(AdvancedDeclarativeBase, CommonTableAttributes):
    __tablename__ = "user_roles"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
