import logging
import traceback

from fastapi import Depends, Request

from .authentication import Authentication
from .authentication import setup as setup_authentication
from .location import LocationService
from .location import setup as setup_location
from .organization import OrganizationService
from .organization import setup as setup_organization
from .role import RoleService
from .role import setup as setup_role
from .taxonomy import TaxonomyService
from .taxonomy import setup as setup_taxonomy
from .user import UserService
from .user import setup as setup_user
from .user_email_token import UserEmailTokenService
from .user_email_token import setup as setup_user_email_token

__services__ = [
    (Authentication, setup_authentication),
    (LocationService, setup_location),
    (OrganizationService, setup_organization),
    (RoleService, setup_role),
    (TaxonomyService, setup_taxonomy),
    (UserService, setup_user),
    (UserEmailTokenService, setup_user_email_token),
]

from t2c_backend.core.db import get_db_session


async def get_services(request: Request, session=Depends(get_db_session)):
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    for service, service_setup in __services__:
        try:
            service_setup(request.app, session=session)
        except Exception as e:
            logging.warn(f"Failed to load service {service} with error {e}.")
            logging.error(traceback.format_exc())
    return request.app.services
