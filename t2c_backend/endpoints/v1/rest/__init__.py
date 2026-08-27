from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest import (
    asset,
    asset_pass,
    asset_type,
    asset_type_category,
    audit,
    authentication,
    dashboard,
    health,
    instruction_manual,
    location,
    organization,
    product_pass_type,
    register,
    service,
    token,
    typeplate,
    user,
)

router = APIRouter(prefix="/v1")

router.include_router(asset.router, tags=["asset"])
router.include_router(asset_pass.router, tags=["asset-pass"])
router.include_router(asset_type.router, tags=["asset-type"])
router.include_router(asset_type_category.router, tags=["asset-type-category"])
router.include_router(audit.router, tags=["audit"])
router.include_router(authentication.router, tags=["authentication"])
router.include_router(health.router, tags=["health"])
router.include_router(location.router, tags=["location"])
router.include_router(organization.router, tags=["organization"])
router.include_router(register.router, tags=["register"])
router.include_router(token.router, tags=["token"])
router.include_router(user.router, tags=["user"])
router.include_router(typeplate.router, tags=["typeplate"])
router.include_router(instruction_manual.router, tags=["instruction-manual"])
router.include_router(service.router, tags=["service"])
router.include_router(dashboard.router, tags=["dashboard"])
router.include_router(product_pass_type.router, tags=["product-pass-type"])
