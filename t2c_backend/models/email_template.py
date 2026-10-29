from sqlalchemy import BigInteger, Enum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from t2c_backend.core.db import AdvancedDeclarativeBase, BigIntPrimaryKey, CommonTableAttributes
from t2c_backend.utils.enums import ENVIRONMENT, EmailTemplateType, Language


class EmailTemplate(BigIntPrimaryKey, CommonTableAttributes, AdvancedDeclarativeBase):
    __tablename__ = "email_templates"

    __table_args__ = (
        UniqueConstraint(
            "type",
            "language",
            "environment",
            name="_type_language_environment_unique",
        ),
    )

    type: Mapped[EmailTemplateType] = mapped_column(Enum(EmailTemplateType), nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language), nullable=False)
    environment: Mapped[ENVIRONMENT] = mapped_column(Enum(ENVIRONMENT), nullable=False)
    template_slug: Mapped[str] = mapped_column(Text(), nullable=False)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    from_name: Mapped[str] = mapped_column(Text(), nullable=False)
