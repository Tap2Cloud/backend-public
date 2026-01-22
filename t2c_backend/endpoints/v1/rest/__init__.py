from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest import (
    asset_type,
    asset_type_category,
    authentication,
    health,
    location,
    organization,
    register,
    taxonomy,
    token,
    user,
)

router = APIRouter(prefix="/v1")

router.include_router(authentication.router, tags=["authentication"])
router.include_router(asset_type_category.router, tags=["asset-type-category"])
router.include_router(asset_type.router, tags=["asset-type"])
router.include_router(health.router, tags=["health"])
router.include_router(location.router, tags=["location"])
router.include_router(organization.router, tags=["organization"])
router.include_router(register.router, tags=["register"])
router.include_router(taxonomy.router, tags=["taxonomy"])
router.include_router(token.router, tags=["token"])
router.include_router(user.router, tags=["user"])
