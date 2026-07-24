import datetime
import uuid

from fastapi import APIRouter, Depends, File, Form, Path, Query, Response, UploadFile
from fastapi.responses import StreamingResponse

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.schemas.v1.typeplates import (
    AssetTypeTypeplateResponse,
    TypeplateImage,
    TypeplateResponse,
    UpdateTypeplateRequest,
)
from t2c_backend.services import get_services
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.get(
    "/typeplate/images",
    operation_id="list typeplate images",
    response_model=list[TypeplateImage],
    status_code=200,
)
async def list_typeplates(
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"typeplate_read": True})),
    services: DictContainer = Depends(get_services),
):
    return [
        TypeplateImage.from_model(images)
        for images in await services.typeplate_service.get_typeplate_images()
    ]


@router.get(
    "/typeplate",
    operation_id="list typeplates",
    response_model=CustomPage[AssetTypeTypeplateResponse],
    status_code=200,
)
async def list_typeplate_details(
    q: str = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    typeplate_created_start_date: datetime.date = None,
    typeplate_created_end_date: datetime.date = None,
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"typeplate_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.typeplate_service.list_typeplates(
        q=q,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        typeplate_created_start_date=typeplate_created_start_date,
        typeplate_created_end_date=typeplate_created_end_date,
        location_id=token.location_id,
    )


@router.put("/typeplate/{typeplateId}", operation_id="update typeplate", status_code=200)
async def update_typeplate(
    typeplate_id: int = Path(..., alias="typeplateId"),
    typeplate_data: UpdateTypeplateRequest = Form(...),
    eu_file: UploadFile | None = File(None),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"typeplate_update": True})),
    services: DictContainer = Depends(get_services),
):
    await services.typeplate_service.update_typeplate(
        typeplate_id=typeplate_id,
        typeplate_data=typeplate_data,
        eu_file=eu_file,
        typeplate_images=typeplate_data.typeplate_images,
        user_id=token.user_id,
        location_id=token.location_id,
        organization_id=token.organization_id,
    )


@router.get(
    "/typeplate/{typeplateId}",
    operation_id="get typeplate by id",
    response_model=TypeplateResponse,
    status_code=200,
)
async def get_typeplate_details_by_id(
    typeplate_id: int = Path(..., alias="typeplateId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"typeplate_read": True})),
    services: DictContainer = Depends(get_services),
):
    typeplate = await services.typeplate_service.get_typeplate_details_by_id(
        typeplate_id=typeplate_id,
    )

    return TypeplateResponse.convert(
        fields=typeplate,
        eu_file_data=typeplate.documents,
        typeplate_images=[img.typeplate_image for img in typeplate.typeplate_images],
    )


@router.delete(
    "/typeplate/document/{typeplateId}/{documentId}",
    operation_id="delete typeplate document",
    status_code=204,
)
async def delete_typeplate_document(
    typeplate_id: int = Path(..., alias="typeplateId"),
    document_id: str = Path(..., alias="documentId"),
    token: AccessToken = Depends(
        JWTAPIAccessTokenBearer(permissions={"typeplate_document_delete": True})
    ),
    services: DictContainer = Depends(get_services),
):
    await services.typeplate_service.delete_typeplate_document(
        typeplate_id=typeplate_id,
        document_id=document_id,
        location_id=token.location_id,
        organization_id=token.organization_id,
    )
    return Response(status_code=204)


@router.get(
    "/typeplate/docuemnt/{typeplateId}/{euFileId}",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "File was downloaded successfully.",
            "content": {
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                    }
                }
            },
        }
    },
    operation_id="get typeplate document",
    status_code=200,
)
async def get_typeplate_document(
    typeplate_id: int = Path(..., alias="typeplateId"),
    eu_file_id: uuid.UUID = Path(..., alias="euFileId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"typeplate_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.typeplate_service.get_typeplate_document(
        eu_file_id=eu_file_id,
        typeplate_id=typeplate_id,
        organization_id=token.organization_id,
    )
