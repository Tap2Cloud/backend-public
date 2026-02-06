from uuid import uuid4

from sqlalchemy.orm import joinedload, selectinload

from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Location, Organization, UserRole
from t2c_backend.models.user import User, UserInvite, UserInviteRole
from t2c_backend.schemas.v1.location import LocationCreateRequest, LocationUpdateRequest
from t2c_backend.utils.enums import Role, Status
from t2c_backend.utils.errors import AlreadyExistsError, InvitationTokenExpiredError, NotFoundError


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
            street=location_data.street,
            postcode=location_data.postcode,
            city=location_data.city,
            country=location_data.country,
            region=location_data.region,
            tel_number=location_data.tel_number,
            mobile_number=location_data.mobile_number,
            fax_number=location_data.fax_number,
            email=location_data.email,
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
            location_id, options=[selectinload(Location.organization)]
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
            options=[joinedload(Location.organization)],
            organization_id=organization_id,
        )

    async def get_all_user_location(self, organization_id: int):
        return await self.repository.list(organization_id=organization_id)

    async def location_invite_user(
        self, inviter_id: int, invitee_email: str, location_id: int, roles: list[Role]
    ):
        user_invite = await self.app.services.user_service.user_invite_repository.save(
            UserInvite(
                inviter_id=inviter_id,
                invitee_email=invitee_email,
                location_id=location_id,
                token=uuid4().hex,
                status=Status.pending,
            )
        )
        [
            await self.app.services.user_service.user_invite_role_repository.save(
                UserInviteRole(
                    role_id=r.id,
                    invitee_id=user_invite.id,
                )
            )
            for r in roles
        ]

        return user_invite

    async def location_accept_invite_user(self, accept_invite_data):
        db_user_invite = (
            await self.app.services.user_service.user_invite_repository.get_one_or_none(
                options=[joinedload(UserInvite.invitee_roles)], token=accept_invite_data.token
            )
        )

        if db_user_invite.status != Status.pending:
            raise AlreadyExistsError(f"User has already {db_user_invite.status} invitation")

        db_user_invite.status = Status.accepted
        await self.app.services.user_service.user_invite_repository.save(db_user_invite)

        if self.app.services.user_service._is_token_expired(db_user_invite):
            raise InvitationTokenExpiredError(
                "Your token has expired. "
                "Please contact the administrator to request a new invitation."
            )

        salt, hashed_password = self.app.services.authentication.generate_encoded_password(
            accept_invite_data.password
        )

        user = await self.app.services.user_service.repository.save(
            User(
                email=db_user_invite.invitee_email,
                hashed_password=hashed_password,
                salt=salt,
                first_name=accept_invite_data.first_name,
                last_name=accept_invite_data.last_name,
                location_id=db_user_invite.location_id,
                is_email_verified=True,
            )
        )

        [
            await self.app.services.user_service.user_role_repository.save(
                UserRole(
                    role_id=user_role.id,
                    user_id=user.id,
                )
            )
            for user_role in db_user_invite.invitee_roles
        ]

        return await self.app.services.user_service.repository.get_one_or_none(
            options=[
                joinedload(User.location)
                .joinedload(Location.organization)
                .joinedload(Organization.taxonomy),
                joinedload(User.roles),
            ],
            id=user.id,
        )

    async def location_re_invite_user(self, invite_token: str):
        db_user_invite = (
            await self.app.services.user_service.user_invite_repository.get_one_or_none(
                options=[joinedload(UserInvite.invitee_roles)], token=invite_token
            )
        )
        if not db_user_invite:
            raise NotFoundError(f"Invitation token '{invite_token}' not found")

        return await self.location_invite_user(
            db_user_invite.inviter_id,
            db_user_invite.invitee_email,
            db_user_invite.location_id,
            db_user_invite.invitee_roles,
        )

    async def location_reject_invite_user(self, invite_token: str):
        db_user_invite = (
            await self.app.services.user_service.user_invite_repository.get_one_or_none(
                options=[joinedload(UserInvite.invitee_roles)], token=invite_token
            )
        )
        if not db_user_invite or db_user_invite.status != Status.pending:
            raise NotFoundError(f"Invitation token '{invite_token}' not found")

        if self.app.services.user_service._is_token_expired(db_user_invite):
            raise InvitationTokenExpiredError(
                "Your token has expired. "
                "Please contact the administrator to request a new invitation."
            )

        db_user_invite.status = Status.rejected
        return await self.app.services.user_service.user_invite_repository.save(db_user_invite)


def setup(app, session, *args, **kwargs):
    return app.add_service(LocationService(app, session), session.info["session_id"])
