import json

from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.datastructures import UploadFile

from t2c_backend.models import ProductPassType as ProductPassTypeModel


class ProductPassType(BaseModel):
    id: int
    name: str
    display_name: str = Field(..., alias="displayName")

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

    @staticmethod
    def from_model(product_pass_type: ProductPassTypeModel) -> "ProductPassType":
        return ProductPassType(
            id=product_pass_type.id,
            name=product_pass_type.name,
            displayName=product_pass_type.display_name,
        )

    @staticmethod
    def from_list(product_pass_types: list["ProductPassTypeModel"]) -> list["ProductPassType"]:
        return [ProductPassType.from_model(ff) for ff in product_pass_types]

    @staticmethod
    def to_orm(product_pass_type: "ProductPassType") -> ProductPassTypeModel:
        return ProductPassTypeModel(
            id=product_pass_type.id,
            name=product_pass_type.name,
            display_name=product_pass_type.display_name,
        )
