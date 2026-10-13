from fastapi import APIRouter

from t2c_backend.endpoints.v1.rest.asset_pass import gs1_router

open_router = APIRouter()

open_router.include_router(gs1_router, tags=["asset-pass"])
