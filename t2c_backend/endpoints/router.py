from fastapi import APIRouter

from ..endpoints.v1 import rest as v1_rest_router

api_router = APIRouter()
ws_router = APIRouter()

api_router.include_router(v1_rest_router.router)
