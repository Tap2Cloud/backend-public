import logging
import traceback

from fastapi import Depends, Request

from .asset import AssetService
from .asset import setup as setup_asset
from .asset_type import AssetTypeService
from .asset_type import setup as setup_asset_type
from .asset_type_category import AssetTypeCategoryService
from .asset_type_category import setup as setup_asset_type_category
from .audit import AuditService
from .audit import setup as setup_audit
from .authentication import Authentication
from .authentication import setup as setup_authentication
from .dashboard import DashboardService
from .dashboard import setup as setup_dashboard
from .location import LocationService
from .location import setup as setup_location
from .organization import OrganizationService
from .organization import setup as setup_organization
from .role import RoleService
from .role import setup as setup_role
from .service import ServiceService
from .service import setup as setup_service
from .taxonomy import TaxonomyService
from .taxonomy import setup as setup_taxonomy
from .typeplate import TypeplateService
from .typeplate import setup as setup_typeplate_documents
from .user import UserService
from .user import setup as setup_user
from .user_email_token import UserEmailTokenService
from .user_email_token import setup as setup_user_email_token

__services__ = [
    (AssetService, setup_asset),
    (AssetTypeService, setup_asset_type),
    (AssetTypeCategoryService, setup_asset_type_category),
    (AuditService, setup_audit),
    (Authentication, setup_authentication),
    (DashboardService, setup_dashboard),
    (LocationService, setup_location),
    (OrganizationService, setup_organization),
    (RoleService, setup_role),
    (UserService, setup_user),
    (UserEmailTokenService, setup_user_email_token),
    (TypeplateService, setup_typeplate_documents),
    (ServiceService, setup_service),
    (TaxonomyService, setup_taxonomy),
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
