from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Text,
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
from t2c_backend.core.db.types import ImageType
from t2c_backend.models import role
from t2c_backend.schemas.v1.image import Image
from t2c_backend.utils.enums import TokenType
from t2c_backend.utils.misc import get_full_name


class User(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "users"

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(Text())
    salt: Mapped[str] = mapped_column(Text())

    first_name: Mapped[str] = mapped_column(Text())
    last_name: Mapped[str] = mapped_column(Text())

    email: Mapped[str] = mapped_column(Text(), unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    profile_avatar: Mapped["Image"] = mapped_column(ImageType(), nullable=True)

    location = relationship("Location")
    email_tokens = relationship(
        "UserEmailToken",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    roles: Mapped[list["role.Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
    )
    organization_rented_assets = relationship("OrganizationRentedAsset", back_populates="user")

    def get_full_name(self):
        return get_full_name(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name


class UserEmailToken(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "user_email_verification"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user_token: Mapped[str] = mapped_column(Text(), unique=True, index=True)
    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    type: Mapped[TokenType] = mapped_column(Enum(TokenType), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    user = relationship("User", back_populates="email_tokens", lazy="selectin")
