from collections.abc import Sequence
from math import ceil
from typing import Any

from fastapi_pagination.bases import AbstractParams, BasePage, RawParams
from pydantic import BaseModel, Field


class CustomParams(BaseModel, AbstractParams):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=1000, alias="pageSize", description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.page_size if self.page_size is not None else None,
            offset=self.page_size * (self.page - 1)
            if self.page is not None and self.page_size is not None
            else None,
        )

    @classmethod
    def get_alias(cls, field_name: str):
        field = cls.__pydantic_fields__.get(field_name)

        if field is None:
            raise AttributeError(f"Field {field_name} is not defined")

        return field.alias or field_name


class CustomPage[T](BasePage[T]):
    page: int = Field(strict=True, ge=1, alias=CustomParams.get_alias("page"))
    page_size: int = Field(strict=True, ge=1, alias=CustomParams.get_alias("page_size"))
    pages: int = Field(strict=True, ge=0)

    __params_type__ = CustomParams

    @classmethod
    def create[T](
        cls,
        items: Sequence[T],
        params: CustomParams,
        *,
        total: int | None = None,
        **kwargs: Any,
    ):
        page_size = params.page_size if params.page_size is not None else (total or None)
        page = params.page if params.page is not None else 1

        if page_size in {0, None}:
            pages = 0
        elif total is not None:
            pages = ceil(total / page_size)
        else:
            pages = None

        return cls.model_validate(
            {
                "total": total,
                "items": items,
                "page": page,
                "page_size": page_size,
                "pages": pages,
                **kwargs,
            },
            from_attributes=True,
        )
