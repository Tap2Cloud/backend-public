from fastapi import APIRouter, Depends

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.location import LocationBaseResponse, LocationCreateRequest
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.put("/location", response_model=LocationBaseResponse, status_code=200)
async def update_location(
    location_data: LocationCreateRequest,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    location = await services.location_service.update_location(
        token.location_id,
        location_data,
    )

    return LocationBaseResponse.convert(location, location.organization)


@router.get(
    "/filter/location",
    response_model=list[LocationBaseResponse],
    status_code=200,
)
async def list_location(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return [
        LocationBaseResponse.convert(location, location.organization)
        for location in await services.location_service.list_location(
            organization_id=token.organization_id
        )
    ]
