from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField

from t2c_backend.models import AssetTypeCategory as AssetTypeCategoryModel
from t2c_backend.schemas.v1.asset_type import DisplayAssetType


class DisplayAssetTypeCategoryMapping(BaseModel):
    id: int
    name: str
    asset_types: list[DisplayAssetType] = PydanticField(..., alias="assetTypes")

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(category: AssetTypeCategoryModel) -> "DisplayAssetTypeCategoryMapping":
        return DisplayAssetTypeCategoryMapping(
            id=category.id,
            name=category.name,
            assetTypes=[
                DisplayAssetType.from_model(asset_type) for asset_type in category.asset_type
            ],
        )
