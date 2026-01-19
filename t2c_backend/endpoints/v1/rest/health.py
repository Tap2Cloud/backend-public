from fastapi import APIRouter, Request

from ....schemas.v1.health import Health

router = APIRouter()


@router.get("/health", response_model=Health, name="health")
async def health(request: Request):
    return Health(version=request.app.version, status="OK")
