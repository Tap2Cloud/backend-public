import datetime
import json
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.datastructures import UploadFile

from t2c_backend.models import Audit as AuditModel
from t2c_backend.models import AuditTask as AuditTaskModel
from t2c_backend.models import AuditTaskDocument as AuditTaskDocumentModel
from t2c_backend.utils.enums import AuditTaskStatus


class AuditTaskDocument(BaseModel):
    id: uuid.UUID
    name: str
    content_type: str = Field(..., alias="contentType")
    created_at: int = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(audit_task_document) -> "AuditTaskDocument":
        return AuditTaskDocument(
            id=audit_task_document.id,
            name=audit_task_document.name,
            contentType=audit_task_document.content_type,
            createdAt=int(audit_task_document.created_at.timestamp()),
        )

    @staticmethod
    def to_orm(audit_task_document_response: "AuditTaskDocument") -> AuditTaskDocumentModel:
        created_at = (
            audit_task_document_response.created_at
            if isinstance(audit_task_document_response.created_at, datetime.datetime)
            else datetime.datetime.fromtimestamp(audit_task_document_response.created_at)
        )

        return AuditTaskDocumentModel(
            id=audit_task_document_response.id,
            name=audit_task_document_response.name,
            content_type=audit_task_document_response.content_type,
            created_at=created_at,
        )


class CreateAuditTask(BaseModel):
    task_name: str = Field(..., alias="taskName")
    status: AuditTaskStatus

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, UploadFile):
            return json.loads(value.file.read())
        return value


class AuditTaskResponse(BaseModel):
    id: int
    task_name: str = Field(..., alias="taskName")
    status: str
    documents: list[AuditTaskDocument] = []

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(audit_task: AuditTaskModel, audit_task_documents) -> "AuditTaskResponse":
        atr = AuditTaskResponse(
            id=audit_task.id,
            taskName=audit_task.task_name,
            status=audit_task.status,
        )

        if audit_task_documents:
            atr.documents = [
                AuditTaskDocument.from_model(document) for document in audit_task_documents
            ]

        return atr

    @staticmethod
    def to_orm(audit_task_obj: "AuditTaskResponse") -> AuditTaskModel:
        return AuditTaskModel(
            id=audit_task_obj.id,
            task_name=audit_task_obj.task_name,
            status=audit_task_obj.status,
            documents=[
                AuditTaskDocument.to_orm(doc_response) for doc_response in audit_task_obj.documents
            ]
            if audit_task_obj.documents
            else [],
        )


class CreateAudit(BaseModel):
    inspection_date: int = Field(..., alias="inspectionDate")
    valid_until: int = Field(..., alias="validUntil")
    audit_tasks: list[AuditTaskResponse] = Field(..., alias="auditTasks")

    model_config = ConfigDict(from_attributes=True)


class AuditResponse(BaseModel):
    id: int
    inspection_date: int = Field(..., alias="inspectionDate")
    valid_until: int = Field(..., alias="validUntil")
    audit_tasks: list[AuditTaskResponse] = Field(..., alias="auditTasks")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(audit: AuditModel, audit_tasks: list[AuditTaskModel]) -> "AuditResponse":
        return AuditResponse(
            id=audit.id,
            inspectionDate=int(audit.inspection_date.timestamp()),
            validUntil=int(
                datetime.datetime.combine(audit.valid_until, datetime.time.min).timestamp()
            ),
            auditTasks=[AuditTaskResponse.from_model(task, task.documents) for task in audit_tasks],
        )


class AssetAuditResponse(BaseModel):
    id: int
    manufacturing_date: int = Field(..., alias="manufacturingDate")
    asset_type_name: str = Field(..., alias="assetTypeName")
    asset_type_description: str = Field(..., alias="assetTypeDescription")
    serial_no: str = Field(..., alias="serialNo")
    audits: list[AuditResponse]

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset) -> "AssetAuditResponse":
        return AssetAuditResponse(
            id=asset.id,
            manufacturingDate=int(asset.manufacturing_date.timestamp()),
            assetTypeName=asset.asset_type.name,
            assetTypeDescription=asset.asset_type.description,
            serialNo=asset.serial_no,
            audits=[AuditResponse.from_model(audit, audit.audit_tasks) for audit in asset.audit],
        )
