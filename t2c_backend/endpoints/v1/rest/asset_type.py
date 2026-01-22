from fastapi import APIRouter, Body, Depends, File, Path, Query, Response, UploadFile

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset_type import (
    AssetTypeDocument,
    AssetTypeResponse,
    CreateAssetTypeRequest,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.typeplates import TypeplateImageList
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/asset-type", status_code=201)
async def create_asset_type(
    asset_type_data: CreateAssetTypeRequest = Body(...),
    eu_file: UploadFile = File(None),
    typeplate_images: TypeplateImageList | None = Body(None),
    instruction_manuals: list[UploadFile] = Body(None),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_service.create_asset_type(
        user_id=token.user_id,
        location_id=token.location_id,
        typeplate_images=typeplate_images,
        asset_type_category_id=asset_type_data.asset_type_category_id,
        asset_type_data=asset_type_data.model_dump(),
        eu_file=eu_file,
        instruction_manuals=instruction_manuals,
    )


@router.delete("/asset-type/{assetTypeId}")
async def delete_asset_type_handler(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_service.delete_asset_type(asset_type_id)
    return Response(status_code=204)


@router.get("/asset-type", response_model=CustomPage[AssetTypeResponse], status_code=200)
async def list_asset_types(
    q: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    category: str | None = None,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.list_asset_types(
        q=q,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        category=category,
        organization_id=token.organization_id,
    )


@router.post(
    "/asset-type/{assetTypeId}/documents", response_model=list[AssetTypeDocument], status_code=201
)
async def save_asset_type_document(
    asset_type_document: list[UploadFile] = File(...),
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return [
        AssetTypeDocument.from_model(asset_type_document)
        for asset_type_document in await services.asset_type_service.save_asset_type_document(
            asset_type_id=asset_type_id,
            instruction_manuals=asset_type_document,
            user_id=token.user_id,
            location_id=token.location_id,
        )
    ]


@router.delete("/asset-type/{assetTypeId}/{documentId}", status_code=204)
async def delete_asset_type_document(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    document_id: str = Path(..., alias="documentId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.delete_asset_type_document(
        asset_type_id=asset_type_id,
        document_id=document_id,
    )
