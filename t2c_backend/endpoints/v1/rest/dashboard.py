from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from t2c_backend.core.db import get_db_session
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.models import Typeplate
from t2c_backend.models.asset import Asset
from t2c_backend.models.asset_type import AssetType, AssetTypeDocument
from t2c_backend.models.location import Location
from t2c_backend.models.service import Service
from t2c_backend.schemas.v1.dashboard import DashboardResponse
from t2c_backend.schemas.v1.token import AccessToken

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardResponse, status_code=200)
async def get_dashboard_summary(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    session: AsyncSession = Depends(get_db_session),
):
    query = await session.execute(
        select(
            func.count(distinct(Asset.id)).label("asset_count"),
            func.count(distinct(Asset.asset_type_id)).label("asset_type_count"),
            func.count(distinct(Typeplate.id)).label("typeplate_count"),
            func.count(distinct(AssetTypeDocument.id)).label("instruction_manual_count"),
            func.count(distinct(Service.id)).label("service_count"),
        )
        .join(Location, Location.id == Asset.location_id)
        .outerjoin(Service, Service.asset_id == Asset.id)
        .join(AssetType, AssetType.id == Asset.asset_type_id)
        .outerjoin(Typeplate, Typeplate.asset_type_id == AssetType.id)
        .outerjoin(AssetTypeDocument, AssetTypeDocument.asset_type_id == AssetType.id)
        .where(Location.organization_id == token.organization_id)
    )
    return DashboardResponse.convert(query.first())
