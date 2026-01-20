from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest import health, register

router = APIRouter(prefix="/v1")

router.include_router(health.router, tags=["health"])
router.include_router(register.router, tags=["register"])
