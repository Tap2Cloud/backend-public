import datetime

from fastapi import APIRouter, Depends, Path, Query, Response

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.service import (
    AssetServiceResponse,
    CreateService,
    ServiceResponse,
    UpdateService,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post(
    "/asset/{assetId}/create/service",
    operation_id="create service",
    response_model=ServiceResponse,
    status_code=201,
)
async def create_service(
    service_data: CreateService,
    asset_id: int = Path(..., alias="assetId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return ServiceResponse.convert(
        await services.service_service.create_service(
            service_data=service_data, asset_id=asset_id, location_id=token.location_id
        )
    )


@router.put(
    "/asset/{serviceId}/update/service",
    operation_id="update service",
    response_model=ServiceResponse,
    status_code=200,
)
async def update_service(
    service_data: UpdateService,
    service_id: int = Path(..., alias="serviceId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return ServiceResponse.convert(
        await services.service_service.update_service(
            service_data=service_data, service_id=service_id, location_id=token.location_id
        )
    )


@router.delete("/service/{serviceId}", operation_id="delete service", status_code=204)
async def delete_service_handler(
    service_id: int = Path(..., alias="serviceId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    await services.service_service.delete_service(service_id, token.location_id)
    return Response(status_code=204)


@router.get(
    "/service",
    operation_id="list all services",
    response_model=CustomPage[AssetServiceResponse],
    status_code=200,
)
async def list_service(
    q: str = None,
    sort_by: SortBy | None = SortBy.Latest,
    service_start_date: datetime.date = None,
    service_end_date: datetime.date = None,
    expire_start_date: datetime.date = None,
    expire_end_date: datetime.date = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    # todo searching asset through QRcode(asset_id) is left

    return await services.service_service.list_services(
        q=q,
        sort_by=sort_by,
        service_start_date=service_start_date,
        service_end_date=service_end_date,
        expire_start_date=expire_start_date,
        expire_end_date=expire_end_date,
        page=page,
        page_size=page_size,
        location_id=token.location_id,
    )


@router.get(
    "/service/{serviceId}",
    operation_id="get service by id",
    response_model=AssetServiceResponse,
    status_code=200,
)
async def get_service_details(
    service_id: int = Path(..., alias="serviceId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return AssetServiceResponse.convert(
        await services.service_service.get_service_by_id(service_id, token.organization_id)
    )
