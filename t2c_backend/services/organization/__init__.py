from fastapi import UploadFile
from sqlalchemy.orm import joinedload, make_transient_to_detached

from t2c_backend.core.permissions import ALL_PERMISSIONS
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import (
    Location,
    Organization,
    Role,
    User,
)
from t2c_backend.models.organization import add_location_count, add_role_count, add_user_count
from t2c_backend.schemas.v1.image import Image
from t2c_backend.schemas.v1.location import LocationCreateRequest
from t2c_backend.schemas.v1.taxonomy import Taxonomy
from t2c_backend.utils.enums import Role as RoleEnum
from t2c_backend.utils.errors import AlreadyExistsError, NotFoundError


class OrganizationService:
    _model = Organization

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def create_organization_with_location(
        self,
        name: str,
        number: str,
        email: str,
        taxonomy: Taxonomy,
        logo: UploadFile,
        location_data: LocationCreateRequest,
        user_id: int,
    ):
        user = await self.app.services.user_service.repository.get(
            user_id,
            options=[
                joinedload(User.location).joinedload(Location.organization),
                joinedload(User.roles),
            ],
        )
        is_organization_exists = await self.repository.exists(
            name__ilike=name, taxonomy_id=taxonomy.id
        )
        if is_organization_exists:
            raise AlreadyExistsError(
                msg="An organization with this name already exists in this taxonomy."
            )

        if user.location_id is not None:
            raise AlreadyExistsError(msg="The organization is already exist with this user.")

        make_transient_to_detached(taxonomy)

        organization = await self.repository.save(
            Organization(
                name=name,
                number=number,
                email=email,
                logo=await Image.from_file(logo) if logo else None,
                taxonomy=taxonomy,
            ),
        )

        roles = {
            name: Role(name=name, organization_id=organization.id, permissions=ALL_PERMISSIONS)
            for name, value in RoleEnum.organization_roles()
        }

        await self.app.services.role_service.repository.save_all(roles.values())

        location = await self.app.services.location_service.create_location(
            location_data=location_data,
            user=user,
            role=roles["owner"],
            organization=organization,
        )

        return organization, location

    async def update_organization(
        self,
        organization_id: int,
        name: str | None,
        number: str | None,
        email: str | None,
        logo: UploadFile | None,
    ):
        organization = await self.repository.get(organization_id)

        if not organization:
            raise NotFoundError(f"Organization with ID '{organization_id}' not found")

        is_organization_exists = await self.repository.exists(
            name__ilike=name,
            taxonomy_id=organization.taxonomy_id,
            id__ne=organization.id,
        )

        if is_organization_exists:
            raise AlreadyExistsError(
                msg="An organization with this name already exists in this taxonomy."
            )

        update_fields = {
            "name": name,
            "number": number,
            # "email": email,
            "logo": await Image.from_file(logo) if logo else None,
        }

        # Update fields dynamically if the values are not None
        for field, value in update_fields.items():
            setattr(organization, field, value)

        return await self.repository.save(organization)

    async def get_organization(self, organization_id: int):
        add_location_count(self._model)
        add_user_count(self._model)
        add_role_count(self._model)
        organization_detail = await self.repository.get_one_or_none(id=organization_id)
        if not organization_detail:
            raise NotFoundError("Organization not found")
        return organization_detail

    async def delete_organization(self, organization_id: int) -> bool:
        await self.repository.delete(id=organization_id)
        return True


def setup(app, session, *args, **kwargs):
    return app.add_service(OrganizationService(app, session), session.info["session_id"])
