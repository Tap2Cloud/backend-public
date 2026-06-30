import uuid

from fastapi import APIRouter, Depends, File, Path, Query, Response, UploadFile

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
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"instruction_manual_read": True})
    ),
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


@router.post(
    "/asset-type/{assetTypeId}/documents",
    operation_id="save asset type document",
    response_model=InstructionManualAssetTypeResponse,
    status_code=201,
)
async def save_asset_type_document(
    documents: list[UploadFile] = File(...),
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"instruction_manual_update": True})
    ),
    services: DictContainer = Depends(get_services),
):
    asset_type_details = await services.asset_type_service.save_asset_type_document(
        asset_type_id=asset_type_id,
        documents=documents,
        user_id=token.user_id,
        location_id=token.location_id,
        organization_id=token.organization_id,
    )
    return InstructionManualAssetTypeResponse.convert(
        asset_type=asset_type_details,
        instruction_manuals_data=[document for document in asset_type_details.documents],
    )


@router.delete(
    "/instruction-manual/{assetTypeId}",
    operation_id="delete asset type document",
    status_code=204,
)
async def delete_asset_type_document(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    instruction_manual_ids: list[uuid.UUID] = Query(..., alias="instructionManualId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"instruction_manual_delete": True})
    ),
    services: DictContainer = Depends(get_services),
):
    for instruction_manual in instruction_manual_ids:
        await services.asset_type_service.delete_asset_type_document(
            asset_type_id=asset_type_id,
            document_id=instruction_manual,
            organization_id=token.organization_id,
        )
    return Response(status_code=204)
