from fastapi import APIRouter, Depends, Path
from waygate.fastapi import rate_limit

from t2c_backend.schemas.v1.asset import DetailedAssetPassResponse
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer, interpret, real_ip

router = APIRouter()


@router.get(
    "/{gs1Path:path}",
    operation_id="get asset pass",
    response_model=DetailedAssetPassResponse,
    status_code=200,
)
@rate_limit("5/second", key=real_ip)
async def get_asset_pass_by_pass_id(
    gs1_path: str = Path(..., alias="gs1Path"),
    services: DictContainer = Depends(get_services),
):
    ref = interpret(gs1_path)
    return DetailedAssetPassResponse.from_model(
        await services.asset_service.get_asset_pass_by_pass_id(pass_id=ref.token, gtin=ref.gtin)
    )
