from fastapi import APIRouter, Depends

from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.taxonomy import Taxonomy
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get("/taxonomies", response_model=list[Taxonomy], status_code=200)
async def get_taxonomy_roles(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer()),
    services: DictContainer = Depends(get_services),
):
    return Taxonomy.from_list(await services.taxonomy_service.get_taxonomies())
