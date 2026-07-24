"""location_based_asset_types

Make asset_type_categories and asset_types location-based (instead of
user-based) for ownership/scoping. `user_id` is retained on both tables purely
as a "created by" acknowledgement and is no longer used for scoping.

Revision ID: pkg_0003
Revises: pkg_0002
Create Date: 2026-07-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "pkg_0003"
down_revision: str | Sequence[str] | None = "pkg_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- asset_type_categories -------------------------------------------------
    op.add_column(
        "asset_type_categories",
        sa.Column("location_id", sa.BigInteger(), nullable=True),
    )
    # Backfill location_id from the creating user's current location.
    op.execute(
        """
        UPDATE asset_type_categories AS atc
        SET location_id = u.location_id
        FROM users AS u
        WHERE atc.user_id = u.id
        """
    )
    op.alter_column("asset_type_categories", "location_id", nullable=False)
    op.create_foreign_key(
        "fk_asset_type_categories_location_id_locations",
        "asset_type_categories",
        "locations",
        ["location_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # Ownership is now location-based, so the uniqueness scope moves from the
    # creator (user_id) to the location_id.
    op.drop_constraint(
        "_asset_type_category_name_unique",
        "asset_type_categories",
        type_="unique",
    )
    op.create_unique_constraint(
        "_asset_type_category_name_unique",
        "asset_type_categories",
        ["name", "location_id"],
    )

    # --- asset_types -----------------------------------------------------------
    op.add_column(
        "asset_types",
        sa.Column("location_id", sa.BigInteger(), nullable=True),
    )
    op.execute(
        """
        UPDATE asset_types AS at
        SET location_id = u.location_id
        FROM users AS u
        WHERE at.user_id = u.id
        """
    )
    op.alter_column("asset_types", "location_id", nullable=False)
    op.create_foreign_key(
        "fk_asset_types_location_id_locations",
        "asset_types",
        "locations",
        ["location_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # --- asset_types -----------------------------------------------------------
    op.drop_constraint(
        "fk_asset_types_location_id_locations",
        "asset_types",
        type_="foreignkey",
    )
    op.drop_column("asset_types", "location_id")

    # --- asset_type_categories -------------------------------------------------
    op.drop_constraint(
        "_asset_type_category_name_unique",
        "asset_type_categories",
        type_="unique",
    )
    op.create_unique_constraint(
        "_asset_type_category_name_unique",
        "asset_type_categories",
        ["name", "user_id"],
    )
    op.drop_constraint(
        "fk_asset_type_categories_location_id_locations",
        "asset_type_categories",
        type_="foreignkey",
    )
    op.drop_column("asset_type_categories", "location_id")
