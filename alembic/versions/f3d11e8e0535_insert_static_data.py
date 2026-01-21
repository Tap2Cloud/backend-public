"""Insert static data

Revision ID: f3d11e8e0535
Revises: 1a386f695ecb
Create Date: 2025-12-09 12:12:01.475318

"""

import json
from collections.abc import Sequence

from sqlalchemy.orm import Session

from alembic import op
from t2c_backend.models import Role, Taxonomy
from t2c_backend.utils.enums import Role as RoleEnum

# revision identifiers, used by Alembic.
revision: str = "f3d11e8e0535"
down_revision: str | Sequence[str] | None = "1a386f695ecb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    with open("data/taxonomies.json") as f:
        taxonomies_list = json.load(f)

    new_taxonomies_list = [
        Taxonomy(
            id=taxonomies["id"], name=taxonomies["name"], display_name=taxonomies["display_name"]
        )
        for taxonomies in taxonomies_list
    ]

    session.add_all(new_taxonomies_list)
    session.add(Role(name=str(RoleEnum.super_admin)))

    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    pass
