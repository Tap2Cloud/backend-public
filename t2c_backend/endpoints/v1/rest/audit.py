import datetime

from fastapi import APIRouter, Body, Depends, File, Form, Header, Path, Query, UploadFile

from t2c_backend.core.pagination import CustomPage
from t2c_backend.core.security import JWTAPIAccessTokenBearer
from t2c_backend.schemas.v1.audit import (
    AssetAuditResponse,
    AuditResponse,
    AuditTaskResponse,
    CreateAudit,
    CreateAuditTask,
)
from t2c_backend.schemas.v1.token import AccessToken
from t2c_backend.services import get_services
from t2c_backend.utils.enums import Language as LanguageEnum
from t2c_backend.utils.enums import SortBy
from t2c_backend.utils.misc import DictContainer

router = APIRouter()


@router.post("/audit/task", response_model=AuditTaskResponse, status_code=201)
async def create_audit_task(
    task: CreateAuditTask = Form(...),
    documents: list[UploadFile] = File(None),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_create": True})),
    services: DictContainer = Depends(get_services),
):
    audit_task, saved_documents = await services.audit_service.create_audit_task(
        organization_id=token.organization_id,
        task=task,
        documents=documents,
    )
    return AuditTaskResponse.from_model(audit_task=audit_task, audit_task_documents=saved_documents)


@router.post("/asset/{assetId}/audit", response_model=AuditResponse, status_code=201)
async def create_audit(
    asset_id: int = Path(..., alias="assetId"),
    audit_data: CreateAudit = Body(...),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_create": True})),
    services: DictContainer = Depends(get_services),
):
    (audit, audit_task) = await services.audit_service.create_audit(
        asset_id=asset_id,
        audit_data=audit_data,
        audit_task_data=[
            AuditTaskResponse.to_orm(audit_task) for audit_task in audit_data.audit_tasks
        ],
        user_id=token.user_id,
    )
    return AuditResponse.from_model(audit=audit, audit_tasks=audit_task)


@router.get("/audit", response_model=CustomPage[AssetAuditResponse], status_code=200)
async def get_audit(
    q: str | None = None,
    sort_by: SortBy | None = SortBy.Latest,
    inspection_start_date: datetime.date = None,
    inspection_end_date: datetime.date = None,
    valid_until_start_date: datetime.date = None,
    valid_until_end_date: datetime.date = None,
    is_audit_available: bool = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000, alias="pageSize"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.audit_service.get_audit_list(
        q=q,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        inspection_start_date=inspection_start_date,
        inspection_end_date=inspection_end_date,
        valid_until_start_date=valid_until_start_date,
        valid_until_end_date=valid_until_end_date,
        is_audit_available=is_audit_available,
        location_id=token.location_id,
    )


@router.delete("/audit/{auditId}", status_code=204)
async def delete_audit(
    audit_id: int = Path(..., alias="auditId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_delete": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.audit_service.delete_audit(audit_id, token.location_id)


@router.delete("/audit/task/{auditTaskId}", status_code=204)
async def delete_audit_task(
    audit_task_id: int = Path(..., alias="auditTaskId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_delete": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.audit_service.delete_audit_task(audit_task_id)


@router.get(
    "/audit/{auditId}/task/{auditTaskId}/document/{documentId}/get",
)
async def document_get_download(
    audit_id: int = Path(..., alias="auditId"),
    task_id: int = Path(..., alias="auditTaskId"),
    document_id: str = Path(..., alias="documentId"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.audit_service.document_get_download(
        organization_id=token.organization_id,
        audit_id=audit_id,
        task_id=task_id,
        document_id=document_id,
    )


@router.get("/asset/{assetId}/audit/{auditId}/audit-report")
async def audit_report(
    asset_id: int = Path(..., alias="assetId"),
    audit_id: int = Path(..., alias="auditId"),
    accept_language: LanguageEnum | None = Header(..., alias="Accept-Language"),
    token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"audit_read": True})),
    services: DictContainer = Depends(get_services),
):
    return await services.audit_service.get_audit_report(
        asset_id=asset_id,
        audit_id=audit_id,
        language=accept_language,
    )
