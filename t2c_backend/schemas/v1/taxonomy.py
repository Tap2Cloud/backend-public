import json

from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.datastructures import UploadFile

from t2c_backend.models import Taxonomy as TaxonomyModel


class Taxonomy(BaseModel):
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
    def from_model(taxonomy: TaxonomyModel) -> "Taxonomy":
        return Taxonomy(
            id=taxonomy.id,
            name=taxonomy.name,
            displayName=taxonomy.display_name,
        )

    @staticmethod
    def from_list(taxonomies: list["TaxonomyModel"]) -> list["Taxonomy"]:
        return [Taxonomy.from_model(ff) for ff in taxonomies]

    @staticmethod
    def to_orm(taxonomy: "Taxonomy") -> TaxonomyModel:
        return TaxonomyModel(
            id=taxonomy.id,
            name=taxonomy.name,
            display_name=taxonomy.display_name,
        )
