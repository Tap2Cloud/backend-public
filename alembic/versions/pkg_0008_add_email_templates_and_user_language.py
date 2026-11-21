"""add_email_templates_and_user_language

Revision ID: pkg_0008
Revises: pkg_0007
Create Date: 2026-10-29 12:07:44.270478

"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from t2c_backend.utils.enums import ENVIRONMENT

# revision identifiers, used by Alembic.
revision: str = "pkg_0008"
down_revision: str | Sequence[str] | None = "pkg_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ENUM_TYPES = ("emailtemplatetype", "language", "environment")


def upgrade() -> None:
    """Upgrade schema."""
    language_enum = sa.Enum("en", "de", "es", "fr", "it", "nl", name="language")

    email_templates = op.create_table(
        "email_templates",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "verify_email", "welcome", "forgot_password", "invite", name="emailtemplatetype"
            ),
            nullable=False,
        ),
        sa.Column("language", language_enum, nullable=False),
        sa.Column(
            "environment",
            sa.Enum("TEST", "DEVELOPMENT", "STAGING", "PRODUCTION", name="environment"),
            nullable=False,
        ),
        sa.Column("template_slug", sa.Text(), nullable=False),
        sa.Column("project_id", sa.BigInteger(), nullable=False),
        sa.Column("from_name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "type", "language", "environment", name="_type_language_environment_unique"
        ),
    )
    op.add_column(
        "users",
        sa.Column("language", language_enum, server_default="en", nullable=False),
    )

    with open("data/email_templates.json") as f:
        templates = json.load(f)

    for template in templates:
        template["environment"] = ENVIRONMENT(template["environment"]).name

    op.bulk_insert(email_templates, templates)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "language")
    op.drop_table("email_templates")

    for enum_type in ENUM_TYPES:
        op.execute(f"DROP TYPE IF EXISTS {enum_type}")
