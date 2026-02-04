from fastapi import APIRouter, Depends, Query

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset_type import InstructionManualAssetTypeResponse
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get(
    "/instruction-manual",
    response_model=CustomPage[InstructionManualAssetTypeResponse],
    status_code=200,
)
async def list_instruction_manual(
    q: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    is_video: bool | None = None,
    is_document: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.list_asset_type_documents(
        q=q,
        sort_by=sort_by,
        is_video=is_video,
        is_document=is_document,
        page=page,
        page_size=page_size,
        organization_id=token.organization_id,
    )
