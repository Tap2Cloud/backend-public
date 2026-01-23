import uuid
from datetime import UTC, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
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
from t2c_backend.models.user import User
from t2c_backend.utils.enums import AuditTaskStatus


class Audit(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "audits"

    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )
    valid_until: Mapped[datetime] = mapped_column(Date(), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"))

    asset = relationship("Asset", back_populates="audit")
    user: Mapped["User"] = relationship("User")
    audit_tasks: Mapped[list["AuditTask"]] = relationship("AuditTask", order_by="AuditTask.id")


class AuditTask(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "audit_tasks"

    task_name: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[AuditTaskStatus] = mapped_column(Enum(AuditTaskStatus), nullable=False)
    audit_id: Mapped[int] = mapped_column(
        ForeignKey("audits.id", ondelete="CASCADE"), nullable=True
    )

    documents: Mapped[list["AuditTaskDocument"]] = relationship("AuditTaskDocument")
    audit: Mapped["Audit"] = relationship("Audit", back_populates="audit_tasks")


class AuditTaskDocument(CommonTableAttributes, AdvancedDeclarativeBase, AuditColumns):
    __tablename__ = "audit_task_documents"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "audit_task_id",
            name="_name_audit_task_audit_task_id_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    content_type: Mapped[str] = mapped_column(Text(), nullable=False)
    audit_task_id: Mapped[int] = mapped_column(ForeignKey("audit_tasks.id", ondelete="CASCADE"))

    audit_task = relationship("AuditTask", back_populates="documents")
