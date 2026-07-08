from pydantic import BaseModel, ConfigDict, Field

from t2c_backend.models import Asset as AssetModel
from t2c_backend.schemas.v1.asset_type import AssetTypeResponse, DisplayAssetType
from t2c_backend.schemas.v1.asset_type_category import (
    AssetTypeCategoryResponse,
    DisplayAssetTypeCategory,
)
from t2c_backend.schemas.v1.audit import AuditResponse
from t2c_backend.schemas.v1.location import LocationBaseResponse
from t2c_backend.schemas.v1.taxonomy import Taxonomy
from t2c_backend.utils.enums import AssetStatus


class CreateAsset(BaseModel):
    location: LocationBaseResponse
    device_id: str = Field(..., alias="deviceId")
    status: str
    serial_no: str | None = Field(..., alias="serialNo")
    economic_operator: str = Field(..., alias="economicOperator")
    manufacturing_date: int = Field(..., alias="manufacturingDate")
    asset_type: DisplayAssetType = Field(..., alias="assetType")

    model_config = ConfigDict(from_attributes=True)


class UpdateAsset(BaseModel):
    status: str
    serial_no: str | None = Field(..., alias="serialNo")
    economic_operator: str = Field(..., alias="economicOperator")

    model_config = ConfigDict(from_attributes=True)


class AssetResponse(BaseModel):
    id: int
    location: LocationBaseResponse
    device_id: str = Field(..., alias="deviceId")
    manufacturing_date: int = Field(..., alias="manufacturingDate")
    asset_type: AssetTypeResponse = Field(..., alias="assetType")
    status: str
    serial_no: str | None = Field(..., alias="serialNo")
    economic_operator: str = Field(..., alias="economicOperator")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(asset: AssetModel) -> "AssetResponse":
        attr = AssetResponse(
            id=asset.id,
            location=LocationBaseResponse.convert(asset.location, asset.location.organization),
            deviceId=asset.device_id,
            manufacturingDate=int(asset.manufacturing_date.timestamp()),
            assetType=AssetTypeResponse.convert(
                asset.asset_type,
                [documents for documents in asset.asset_type.documents],
            ),
            status=asset.status,
            serialNo=asset.serial_no,
            economicOperator=asset.economic_operator,
        )

        return attr


class DisplayAsset(BaseModel):
    id: int
    serial_no: str = Field(..., alias="serialNo")
    asset_type: DisplayAssetType = Field(..., alias="assetType")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset: AssetModel) -> "DisplayAsset":
        return DisplayAsset(
            id=asset.id,
            serialNo=asset.serial_no,
            assetType=DisplayAssetType.from_model(asset.asset_type),
        )

    @staticmethod
    def to_orm(asset: "DisplayAsset") -> AssetModel:
        return AssetModel(
            id=asset.id,
            serial_no=asset.serial_no,
            asset_type=DisplayAssetType.to_orm(asset.asset_type),
        )


class AssetPassResponse(BaseModel):
    id: int
    serial_no: str | None = Field(..., alias="serialNo")
    economic_operator: str = Field(..., alias="economicOperator")
    device_id: str = Field(..., alias="deviceId")
    pass_id: str = Field(..., alias="passId")
    asset_type: DisplayAssetType = Field(..., alias="assetType")
    location: LocationBaseResponse = Field(..., alias="location")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset: AssetModel) -> "AssetPassResponse":
        atr = AssetPassResponse(
            id=asset.id,
            serialNo=asset.serial_no,
            economicOperator=asset.economic_operator,
            deviceId=asset.device_id,
            passId=asset.pass_id,
            assetType=DisplayAssetType.from_model(asset.asset_type),
            location=LocationBaseResponse.convert(asset.location, asset.location.organization),
        )

        return atr


class DetailedAssetPassResponse(BaseModel):
    asset_pass: AssetPassResponse = Field(..., alias="assetPass")
    asset_type: AssetTypeResponse = Field(..., alias="assetType")
    asset_type_category: AssetTypeCategoryResponse = Field(..., alias="assetTypeCategory")
    audit: list[AuditResponse]
    taxonomy: Taxonomy

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(asset: AssetModel) -> "DetailedAssetPassResponse":
        return DetailedAssetPassResponse(
            assetPass=AssetPassResponse.from_model(asset),
            assetType=AssetTypeResponse.convert(
                asset.asset_type, [documents for documents in asset.asset_type.documents]
            ),
            assetTypeCategory=AssetTypeCategoryResponse.convert(
                asset.asset_type.asset_type_category
            ),
            taxonomy=Taxonomy.from_model(asset.location.organization.taxonomy),
            audit=[AuditResponse.from_model(audit, audit.audit_tasks) for audit in asset.audit],
        )


class DisplayFilterAssetResponse(BaseModel):
    rented_assets: list["DisplayAsset"] = Field(default_factory=list, alias="rentedAssets")
    owned_assets: list["DisplayAsset"] = Field(default_factory=list, alias="ownedAssets")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(owned_assets, organization_rented_assets) -> "DisplayFilterAssetResponse":
        return DisplayFilterAssetResponse(
            rentedAssets=[
                DisplayAsset.from_model(rented_asset.asset)
                for rented_asset in organization_rented_assets
            ],
            ownedAssets=[DisplayAsset.from_model(asset) for asset in owned_assets],
        )


class SelectiveFilters(BaseModel):
    categories: list[DisplayAssetTypeCategory] | None = None
    status: list[AssetStatus] | None = None
