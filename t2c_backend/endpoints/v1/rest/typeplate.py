import datetime

from fastapi import APIRouter, Depends, Query

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.typeplates import (
    AssetTypeTypeplateResponse,
    TypeplateImage,
)
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get("/typeplate/images", response_model=list[TypeplateImage], status_code=200)
async def list_typeplates(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return [
        TypeplateImage.from_model(images)
        for images in await services.typeplate_service.get_typeplate_images()
    ]


@router.get("/typeplate", response_model=CustomPage[AssetTypeTypeplateResponse], status_code=200)
async def list_typeplate_details(
    q: str = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    typeplate_created_start_date: datetime.date = None,
    typeplate_created_end_date: datetime.date = None,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return await services.typeplate_service.list_typeplates(
        q=q,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        typeplate_created_start_date=typeplate_created_start_date,
        typeplate_created_end_date=typeplate_created_end_date,
        organization_id=token.organization_id,
    )
