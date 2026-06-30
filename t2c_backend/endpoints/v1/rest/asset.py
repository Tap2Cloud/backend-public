from fastapi import APIRouter, Depends, Path, Query, Response

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset import (
    AssetResponse,
    CreateAsset,
    DetailedAssetPassResponse,
    SelectiveFilters,
    UpdateAsset,
)
from t2c_backend.schemas.v1.asset_type import DisplayAssetType
from t2c_backend.schemas.v1.location import LocationBaseResponse
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.errors import NotFoundError
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/asset", operation_id="create asset", status_code=201)
async def create_asset(
    asset_data: CreateAsset,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_create": True})),
    services: DictContainer = Depends(get_services),
):
    # todo if we remove the query, the issue aries when converting Pydantic models to ORM
    #  using to_orm() and passing them to session.merge(), SQLAlchemy treats them as transient
    #  and creates new entries if they don't exist
    asset_type = await services.asset_type_service.repository.get_one_or_none(
        id=asset_data.asset_type.id
    )
    if not asset_type:
        raise NotFoundError(msg="Asset type not found")
    asset_type = DisplayAssetType.to_orm(asset_data.asset_type)

    location = await services.location_service.repository.get_one_or_none(id=asset_data.location.id)
    if not location:
        raise NotFoundError(msg="Location not found")
    location = LocationBaseResponse.to_orm(asset_data.location)

    await services.asset_service.create_asset(
        asset_data=asset_data, asset_type=asset_type, location=location
    )


@router.put("/asset/{assetId}", operation_id="update asset", status_code=200)
async def update_asset(
    asset_data: UpdateAsset,
    asset_id: int = Path(..., alias="assetId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_update": True})),
    services: DictContainer = Depends(get_services),
):
    await services.asset_service.update_asset(updated_asset_data=asset_data, asset_id=asset_id)


@router.delete("/asset/{assetId}", operation_id="delete asset")
async def delete_asset_handler(
    asset_id: int = Path(..., alias="assetId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_delete": True})),
    services: DictContainer = Depends(get_services),
):
    await services.asset_service.delete_asset(asset_id, token.location_id)
    return Response(status_code=204)


@router.put(
    "/asset",
    operation_id="list all asset",
    response_model=CustomPage[AssetResponse],
    status_code=200,
)
async def list_asset(
    selective: SelectiveFilters,
    q: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_read": True})),
    services: DictContainer = Depends(get_services),
):
    # todo searching asset through QRcode(asset_id) is left

    return await services.asset_service.list_assets(
        q=q,
        sort_by=sort_by,
        status=selective.status,
        categories=selective.categories,
        page=page,
        page_size=page_size,
        location_id=token.location_id,
    )


@router.get(
    "/asset/{assetId:int}", operation_id="get asset", response_model=AssetResponse, status_code=200
)
async def get_asset(
    asset_id: int = Path(..., alias="assetId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_read": True})),
    services: DictContainer = Depends(get_services),
):
    return AssetResponse.convert(
        await services.asset_service.get_asset_by_organization_id(asset_id, token.organization_id)
    )


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
