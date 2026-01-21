from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest import health, organization, register, taxonomy

router = APIRouter(prefix="/v1")

router.include_router(health.router, tags=["health"])
router.include_router(register.router, tags=["register"])
router.include_router(organization.router, tags=["organization"])
router.include_router(taxonomy.router, tags=["taxonomy"])
