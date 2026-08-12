from fastapi import APIRouter, Depends

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.product_pass_type import ProductPassType
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get("/product-pass-type", response_model=list[ProductPassType], status_code=200)
async def get_product_pass_types(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return ProductPassType.from_list(
        await services.product_pass_type_service.get_product_pass_types()
    )
