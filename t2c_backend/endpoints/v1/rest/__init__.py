from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest import (
    authentication,
    health,
    organization,
    register,
    taxonomy,
    token,
)

router = APIRouter(prefix="/v1")

router.include_router(authentication.router, tags=["authentication"])
router.include_router(health.router, tags=["health"])
router.include_router(organization.router, tags=["organization"])
router.include_router(register.router, tags=["register"])
router.include_router(taxonomy.router, tags=["taxonomy"])
router.include_router(token.router, tags=["token"])
