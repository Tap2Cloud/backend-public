from sqlalchemy.orm import joinedload, selectinload

from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Location
from t2c_backend.models.organization import Organization as OrganizationModel
from t2c_backend.schemas.v1.location import LocationCreateRequest, LocationUpdateRequest
from t2c_backend.utils.errors import NotFoundError


class LocationService:
    _model = Location

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def create_location(
        self,
        location_data: LocationCreateRequest,
        role,
        organization,
        user,
    ):
        location = Location(
            organization_id=organization.id,
            city=location_data.city,
            country=location_data.country,
        )

        location = await self.repository.save(location)

        user.location_id = location.id
        user.roles.append(role)

        return location

    async def update_location(
        self,
        location_id: int,
        location_data: LocationUpdateRequest,
    ):
        location = await self.repository.get(
            location_id,
            options=[
                selectinload(Location.organization),
                selectinload(Location.organization).selectinload(
                    OrganizationModel.product_pass_type
                ),
            ],
        )

        if not location:
            raise NotFoundError(f"Location with ID '{location_id}' not found")

        for field, value in location_data.model_dump(exclude_unset=True).items():
            setattr(location, field, value)

        return await self.repository.save(location, refresh=True)

    async def get_location_by_user_organization_id(self, organization_id: int, location_id: int):
        return await self.repository.get_one_or_none(
            options=[joinedload(Location.organization)],
            id=location_id,
            organization_id=organization_id,
        )

    async def list_location(self, organization_id: int):
        return await self.repository.list(
            options=[
                joinedload(Location.organization),
                joinedload(Location.organization).selectinload(OrganizationModel.product_pass_type),
            ],
            organization_id=organization_id,
        )

    async def get_all_user_location(self, organization_id: int):
        return await self.repository.list(organization_id=organization_id)


def setup(app, session, *args, **kwargs):
    return app.add_service(LocationService(app, session), session.info["session_id"])
