"""created_by_set_null_on_user_delete

Deleting a user must never delete location-owned data. The `user_id` columns on
location-based entities are only a "created by" acknowledgement, so their
foreign keys are switched from ON DELETE CASCADE to ON DELETE SET NULL (and made
nullable). When a user is removed, these rows survive with user_id = NULL.

Revision ID: pkg_0004
Revises: pkg_0003
Create Date: 2026-07-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "pkg_0004"
down_revision: str | Sequence[str] | None = "pkg_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (table, foreign-key constraint name) for every location-based "created by" user_id.
_TABLES = [
    ("asset_type_categories", "asset_type_categories_user_id_fkey"),
    ("asset_types", "asset_types_user_id_fkey"),
    ("asset_types_documents", "asset_types_documents_user_id_fkey"),
    ("audits", "audits_user_id_fkey"),
    ("typeplate_documents", "typeplate_documents_user_id_fkey"),
    ("documents", "documents_user_id_fkey"),
]


def upgrade() -> None:
    for table, fk_name in _TABLES:
        op.drop_constraint(fk_name, table, type_="foreignkey")
        op.alter_column(table, "user_id", existing_type=sa.BigInteger(), nullable=True)
        op.create_foreign_key(fk_name, table, "users", ["user_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    for table, fk_name in _TABLES:
        op.drop_constraint(fk_name, table, type_="foreignkey")
        op.alter_column(table, "user_id", existing_type=sa.BigInteger(), nullable=False)
        op.create_foreign_key(fk_name, table, "users", ["user_id"], ["id"], ondelete="CASCADE")
