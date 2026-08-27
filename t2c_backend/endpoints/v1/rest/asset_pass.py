from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import StreamingResponse

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset import (
    DetailedAssetPassResponse,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import DocumentFor, SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get(
    "/asset-pass",
    operation_id="list asset pass",
    response_model=CustomPage[DetailedAssetPassResponse],
    status_code=200,
)
async def list_asset_pass(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    sort_by: SortBy | None = SortBy.Latest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"list_asset_pass": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_service.list_asset_pass(
        q=q, page=page, page_size=page_size, organization_id=token.organization_id, sort_by=sort_by
    )


@router.get(
    "/asset-pass/{passId}",
    operation_id="get asset pass",
    response_model=DetailedAssetPassResponse,
    status_code=200,
)
async def get_asset_pass_by_pass_id(
    pass_id: str = Path(..., alias="passId"),
    services: DictContainer = Depends(get_services),
):
    return DetailedAssetPassResponse.from_model(
        await services.asset_service.get_asset_pass_by_pass_id(pass_id)
    )


@router.get(
    "/asset-pass/{passId}/document/{documentFor}/{documentId}",
    operation_id="get asset pass document",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "File was downloaded successfully.",
            "content": {
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                    }
                }
            },
        }
    },
    status_code=200,
)
async def get_asset_pass_document(
    pass_id: str = Path(..., alias="passId"),
    document_for: DocumentFor = Path(..., alias="documentFor"),
    document_id: str = Path(..., alias="documentId"),
    download: bool = Query(False),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_service.get_asset_pass_document(
        pass_id=pass_id,
        document_for=document_for,
        document_id=document_id,
        as_attachment=download,
    )
