"""insert_static_data

Revision ID: pkg_0002
Revises: pkg_0001
Create Date: 2026-03-05 12:25:38.028895

"""

import base64
import json
import mimetypes
import os
from collections.abc import Sequence

from sqlalchemy.orm import Session

from alembic import op
from t2c_backend.models import AssetTypeCategoryGroup, Role, Taxonomy, TypeplateImage
from t2c_backend.schemas.v1.image import Image
from t2c_backend.utils.enums import Role as RoleEnum

# revision identifiers, used by Alembic.
revision: str = "pkg_0002"
down_revision: str | Sequence[str] | None = "pkg_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    with open("data/taxonomies.json") as f:
        taxonomies_list = json.load(f)

    new_taxonomies_list = [
        Taxonomy(name=taxonomies["name"], display_name=taxonomies["display_name"])
        for taxonomies in taxonomies_list
    ]

    image_folder_path = "images"
    image_files = [
        f
        for f in os.listdir(image_folder_path)
        if os.path.isfile(os.path.join(image_folder_path, f))
    ]

    new_typeplate_images = []
    for filename in image_files:
        file_path = os.path.join(image_folder_path, filename)

        with open(file_path, "rb") as f:
            image_content = f.read()

        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"

        image_obj = Image(
            image=base64.b64encode(image_content).decode("ascii"),
            filename=filename,
            content_type=content_type,
        )

        new_typeplate_images.append(TypeplateImage(name=filename, image=image_obj))

    with open("data/asset_type_category_group.json") as f:
        asset_type_category_group_list = json.load(f)

    new_asset_type_category_group_list = [
        AssetTypeCategoryGroup(
            id=asset_type_category_group["id"],
            name=asset_type_category_group["name"],
            order=asset_type_category_group["order"],
        )
        for asset_type_category_group in asset_type_category_group_list
    ]

    session.add_all(new_asset_type_category_group_list)
    session.add_all(new_taxonomies_list)
    session.add_all(new_typeplate_images)
    session.add(Role(name=str(RoleEnum.super_admin)))

    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    pass
