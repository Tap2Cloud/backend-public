from fastapi import APIRouter, Depends, Path, Query, Response

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset_type_category import (
    AssetTypeCategoryGroupResponse,
    AssetTypeCategoryResponse,
    CreateAssetTypeCategoryRequest,
    DisplayAssetTypeCategory,
    UpdateAssetTypeCategoryRequest,
)
from t2c_backend.schemas.v1.filter_asset_type_category_mapping import (
    DisplayAssetTypeCategoryMapping,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post(
    "/asset-type-category",
    operation_id="create asset type category",
    response_model=AssetTypeCategoryResponse,
    status_code=200,
)
async def create_asset_type_category(
    form_data: CreateAssetTypeCategoryRequest,
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_create": True})
    ),
    services: DictContainer = Depends(get_services),
):
    db_form = await services.asset_type_category_service.create_asset_type_category(
        token.user_id,
        token.location_id,
        form_data.model_dump(),
    )
    return AssetTypeCategoryResponse.convert(db_form)


@router.get(
    "/asset-type-category",
    operation_id="get asset type category",
    response_model=CustomPage[AssetTypeCategoryResponse],
    status_code=200,
)
async def get_asset_type_categories(
    query: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_read": True})
    ),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_category_service.list_asset_type_categories(
        q=query,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        location_id=token.location_id,
    )


@router.patch(
    "/asset-type-category/{assetTypeCategoryId}",
    operation_id="update asset type category",
    response_model=AssetTypeCategoryResponse,
    status_code=200,
)
async def update_asset_type_category(
    updated_asset_type_category: UpdateAssetTypeCategoryRequest,
    asset_type_category_id: int = Path(..., alias="assetTypeCategoryId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_update": True})
    ),
    services: DictContainer = Depends(get_services),
):
    return AssetTypeCategoryResponse.convert(
        await services.asset_type_category_service.update_asset_type_category(
            asset_type_category_id=asset_type_category_id,
            updated_asset_type_category_data=updated_asset_type_category,
            location_id=token.location_id,
        )
    )


@router.delete(
    "/asset-type-category/{assetTypeCategoryId}",
    operation_id="delete asset type category",
    status_code=200,
)
async def delete_asset_type_category(
    asset_type_category_id: int = Path(..., alias="assetTypeCategoryId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_delete": True})
    ),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_category_service.delete_asset_type_category(
        asset_type_category_id, token.location_id
    )
    return Response(status_code=200)


@router.get(
    "/asset-type-category-group",
    operation_id="get asset type category groups",
    response_model=list[AssetTypeCategoryGroupResponse],
    status_code=200,
)
async def get_asset_type_category_groups(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return AssetTypeCategoryGroupResponse.from_list(
        await services.asset_type_category_service.asset_type_category_groups_repository.list()
    )


@router.get(
    "/filter/asset-type-category",
    operation_id="list asset type category",
    response_model=list[DisplayAssetTypeCategory],
    status_code=200,
)
async def list_asset_type_categories(
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_read": True})
    ),
    services: DictContainer = Depends(get_services),
):
    return [
        DisplayAssetTypeCategory.from_model(asset_type_category)
        for asset_type_category in await services.asset_type_category_service.get_asset_type_categories(  # noqa E501
            token.location_id
        )
    ]


@router.get(
    "/asset-type-category/{assetTypeCategoryId}",
    operation_id="get asset type category by id",
    response_model=AssetTypeCategoryResponse,
    status_code=200,
)
async def get_asset_type_category(
    asset_type_category_id: int = Path(..., alias="assetTypeCategoryId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_read": True})
    ),
    services: DictContainer = Depends(get_services),
):
    return AssetTypeCategoryResponse.convert(
        await services.asset_type_category_service.get_asset_type_category(
            location_id=token.location_id, asset_type_category_id=asset_type_category_id
        )
    )


@router.get(
    "/filter/asset-type-category/mapping",
    operation_id="get asset type category mapping",
    response_model=list[DisplayAssetTypeCategoryMapping],
    status_code=200,
)
async def filter_asset_type(
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"asset_type_category_read": True})
    ),
    services: DictContainer = Depends(get_services),
):
    return [
        DisplayAssetTypeCategoryMapping.from_model(asset_type)
        for asset_type in await services.asset_type_category_service.list_asset_type_category(
            location_id=token.location_id
        )
    ]
