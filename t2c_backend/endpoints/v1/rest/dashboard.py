from fastapi import APIRouter, Depends

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.dashboard import DashboardResponse
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get(
    "/dashboard/summary",
    operation_id="dashboard statistics",
    response_model=DashboardResponse,
    status_code=200,
)
async def get_dashboard_summary(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    (
        asset_count,
        asset_type_count,
        typeplate_count,
        instruction_manual_count,
        service_count,
        audit_count,
    ) = await services.dashboard_service.get_dashboard_statistics(
        organization_id=token.organization_id
    )
    return DashboardResponse.convert(
        asset_type_count=asset_type_count,
        typeplate_count=typeplate_count,
        asset_count=asset_count,
        service_count=service_count,
        instruction_manual_count=instruction_manual_count,
        inspection=audit_count,
    )
