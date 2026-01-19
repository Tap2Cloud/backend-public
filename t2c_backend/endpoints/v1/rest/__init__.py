from fastapi import APIRouter

from ....endpoints.v1.rest import health

router = APIRouter(prefix="/v1")

router.include_router(health.router, tags=["health"])
