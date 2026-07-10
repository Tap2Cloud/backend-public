from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest.asset_pass import router as asset_pass_router

open_router = APIRouter()

open_router.include_router(asset_pass_router, tags=["asset-pass"])
