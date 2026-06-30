import uuid

from fastapi import APIRouter, Depends, File, Form, Path, Query, Response, UploadFile

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.asset_type import (
    AssetTypeResponse,
    CreateAssetTypeRequest,
    SelectiveFilters,
    UpdateAssetTypeRequest,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import DocumentFor, SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post(
    "/asset-type",
    operation_id="create asset type",
    status_code=204,
)
async def create_asset_type(
    asset_type_data: CreateAssetTypeRequest = Form(...),
    eu_file: UploadFile | str | None = File(None),
    instruction_manuals: list[UploadFile] = File(None),
    custom_media_fields: list[UploadFile] = File(None),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_create": True})),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_service.create_asset_type(
        user_id=token.user_id,
        location_id=token.location_id,
        organization_id=token.organization_id,
        typeplate_images=asset_type_data.typeplate_images,
        asset_type_category_id=asset_type_data.asset_type_category_id,
        asset_type_data=asset_type_data.model_dump(),
        eu_file=eu_file,
        instruction_manuals=instruction_manuals,
        custom_media_fields=custom_media_fields,
    )


@router.put("/asset-type/{assetTypeId}", operation_id="update asset type", status_code=200)
async def update_asset_type(
    asset_type_data: UpdateAssetTypeRequest,
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_update": True})),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_service.update_asset_type(
        asset_type_id, asset_type_data, token.location_id
    )
    return Response(status_code=200)


@router.delete("/asset-type/{assetTypeId}", operation_id="delete asset type")
async def delete_asset_type_handler(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_delete": True})),
    services: DictContainer = Depends(get_services),
):
    await services.asset_type_service.delete_asset_type(
        asset_type_id=asset_type_id, location_id=token.location_id
    )
    return Response(status_code=204)


@router.put(
    "/asset-type",
    operation_id="list asset types",
    response_model=CustomPage[AssetTypeResponse],
    status_code=200,
)
async def list_asset_types(
    selective: SelectiveFilters,
    query: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.list_asset_types(
        q=query,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        categories=selective.categories,
        organization_id=token.organization_id,
    )


@router.get(
    "/asset-type/{assetTypeId}",
    operation_id="get asset type by id",
    response_model=AssetTypeResponse,
    status_code=200,
)
async def get_asset_type_by_id(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_read": True})),
    services: DictContainer = Depends(get_services),
):
    asset_type_details = await services.asset_type_service.get_asset_type_by_id(
        asset_type_id=asset_type_id, location_id=token.location_id
    )
    return AssetTypeResponse.convert(
        asset_type=asset_type_details,
        instruction_manuals_data=[document for document in asset_type_details.documents],
    )


@router.post(
    "/asset-type/{assetTypeId}/custom-field/documents",
    operation_id="save asset type custom field document",
    response_model=AssetTypeResponse,
    status_code=201,
)
async def save_asset_type_custom_field_document(
    custom_field_id: int = Form(..., alias="customFieldId"),
    documents: UploadFile = File(...),
    asset_type_id: int = Path(..., alias="assetTypeId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_update": True})),
    services: DictContainer = Depends(get_services),
):
    asset_type_details = await services.asset_type_service.save_asset_type_custom_field_document(
        asset_type_id=asset_type_id,
        custom_field_id=custom_field_id,
        documents=documents,
        organization_id=token.organization_id,
    )
    return AssetTypeResponse.convert(
        asset_type=asset_type_details,
        instruction_manuals_data=[document for document in asset_type_details.documents],
    )


@router.delete(
    "/asset-type/custom-field/{assetTypeId}/{documentId}",
    operation_id="delete asset type custom field document",
    status_code=204,
)
async def delete_asset_type_custom_field_document(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    document_id: int = Path(..., alias="documentId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_update": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.delete_asset_type_custom_field_document(
        asset_type_id=asset_type_id,
        document_id=document_id,
        organization_id=token.organization_id,
    )


@router.get(
    "/asset-type/{assetTypeId}/get/document/{instructionManualId}/{documentName}",
    operation_id="get asset type document",
)
async def get_asset_type_document(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    instruction_manual_id: uuid.UUID = Path(..., alias="instructionManualId"),
    document_name: str = Path(..., alias="documentName"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.get_asset_type_document(
        asset_type_id=asset_type_id,
        organization_id=token.organization_id,
        document_type=DocumentFor.InstructionManualDocuments,
        document_id=instruction_manual_id,
        document_name=document_name,
    )


@router.get(
    "/asset-type/{assetTypeId}/get/custom-field/document/{documentId}/{documentName}",
    operation_id="get asset type custom field document",
)
async def get_asset_type_custom_field_document(
    asset_type_id: int = Path(..., alias="assetTypeId"),
    document_id: int = Path(..., alias="documentId"),
    document_name: str = Path(..., alias="documentName"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_type_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_type_service.get_asset_type_document(
        asset_type_id=asset_type_id,
        organization_id=token.organization_id,
        document_type=DocumentFor.AssetTypeFieldSpecificDocuments,
        document_id=document_id,
        document_name=document_name,
    )
