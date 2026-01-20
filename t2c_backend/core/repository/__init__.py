from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import Column, ColumnElement, and_, delete, exists, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.util import AliasedClass

from t2c_backend.core.db import AdvancedDeclarativeBase

ModelType = TypeVar("ModelType", bound=AdvancedDeclarativeBase)


class BaseRepository:
    _SUPPORTED_FILTERS = {
        "eq": lambda column: column.__eq__,
        "gt": lambda column: column.__gt__,
        "lt": lambda column: column.__lt__,
        "gte": lambda column: column.__ge__,
        "lte": lambda column: column.__le__,
        "ne": lambda column: column.__ne__,
        "is": lambda column: column.is_,
        "is_not": lambda column: column.is_not,
        "like": lambda column: column.like,
        "notlike": lambda column: column.notlike,
        "ilike": lambda column: column.ilike,
        "notilike": lambda column: column.notilike,
        "startswith": lambda column: column.startswith,
        "endswith": lambda column: column.endswith,
        "contains": lambda column: column.contains,
        "match": lambda column: column.match,
        "between": lambda column: column.between,
        "in": lambda column: column.in_,
        "not_in": lambda column: column.not_in,
        "or": lambda column: column.or_,
        "not": lambda column: column.not_,
    }

    def __init__(
        self,
        app,
        session: AsyncSession | async_scoped_session[AsyncSession],
        model: type[ModelType],
    ) -> None:
        self.app = app
        self.session = session
        self.model = model

    @staticmethod
    def _get_sqlalchemy_filter(
        operator: str,
        value: Any,
    ) -> Callable[[Column[Any]], Callable[..., ColumnElement[bool]]] | None:
        if operator in {"in", "not_in", "between"}:
            if not isinstance(value, tuple | list | set):
                raise ValueError(f"<{operator}> filter must be tuple, list or set")
        return BaseRepository._SUPPORTED_FILTERS.get(operator)

    @classmethod
    def _get_column(cls, model: type[ModelType] | AliasedClass, field_name: str) -> Column[Any]:
        model_column = getattr(model, field_name, None)
        if model_column is None:
            raise ValueError(f"Invalid filter column: {field_name}")
        return model_column

    @classmethod
    def _handle_simple_filter(
        cls, model: type[ModelType] | AliasedClass, key: str, value: Any
    ) -> list[ColumnElement]:
        col = getattr(model, key, None)
        return [col == value] if col is not None else []

    @classmethod
    def _handle_or_filter(cls, col: Column, value: dict) -> list[ColumnElement]:
        if not isinstance(value, dict):  # pragma: no cover
            raise ValueError("OR filter value must be a dictionary")

        or_conditions = []
        for or_op, or_value in value.items():
            sqlalchemy_filter = cls._get_sqlalchemy_filter(or_op, or_value)
            if sqlalchemy_filter:
                condition = (
                    sqlalchemy_filter(col)(*or_value)
                    if or_op == "between"
                    else sqlalchemy_filter(col)(or_value)
                )
                or_conditions.append(condition)

        return [or_(*or_conditions)] if or_conditions else []

    @classmethod
    def _handle_not_filter(cls, col: Column, value: dict) -> list[ColumnElement[bool]]:
        """Handle NOT conditions (e.g., age__not={'eq': 20, 'between': (30, 40)})."""
        if not isinstance(value, dict):  # pragma: no cover
            raise ValueError("NOT filter value must be a dictionary")

        not_conditions = []
        for not_op, not_value in value.items():
            sqlalchemy_filter = cls._get_sqlalchemy_filter(not_op, not_value)
            if sqlalchemy_filter is None:  # pragma: no cover
                continue

            condition = (
                sqlalchemy_filter(col)(*not_value)
                if not_op == "between"
                else sqlalchemy_filter(col)(not_value)
            )
            not_conditions.append(condition)

        return [and_(*(not_(cond) for cond in not_conditions))] if not_conditions else []

    @classmethod
    def _handle_standard_filter(
        cls, col: Column[Any], operator: str, value: Any
    ) -> list[ColumnElement[bool]]:
        """Handle standard comparison operators (e.g., age__gt=18)."""
        sqlalchemy_filter = cls._get_sqlalchemy_filter(operator, value)
        if sqlalchemy_filter is None:  # pragma: no cover
            return []

        condition = (
            sqlalchemy_filter(col)(*value)
            if operator == "between"
            else sqlalchemy_filter(col)(value)
        )
        return [condition]

    @staticmethod
    def parse_filters(model: type[ModelType] | AliasedClass, **kwargs) -> list[ColumnElement]:
        filters = []

        for key, value in kwargs.items():
            if "__" not in key:
                filters.extend(BaseRepository._handle_simple_filter(model, key, value))
                continue

            field_name, operator = key.rsplit("__", 1)
            model_column = BaseRepository._get_column(model, field_name)

            if operator == "or":
                filters.extend(BaseRepository._handle_or_filter(model_column, value))
            elif operator == "not":
                filters.extend(BaseRepository._handle_not_filter(model_column, value))
            else:
                filters.extend(
                    BaseRepository._handle_standard_filter(model_column, operator, value)
                )

        return filters

    async def save(self, instance: ModelType, refresh: bool = False) -> ModelType:
        self.session.info["engine"] = "writer"
        self.session.add(instance)
        await self.session.flush([instance])
        if refresh:
            await self.session.refresh(instance)
        return instance

    async def save_all(self, instances: list[ModelType], refresh: bool = False) -> list[ModelType]:
        self.session.info["engine"] = "writer"
        self.session.add_all(instances)
        await self.session.flush(instances)
        if refresh:
            [await self.session.refresh(instance) for instance in instances]
        return instances

    async def get_one_or_none(
        self,
        options: list | None = None,
        join: list[InstrumentedAttribute] | None = None,
        **kwargs,
    ) -> ModelType:
        filters = self.parse_filters(model=self.model, **kwargs)
        statement = select(self.model)

        if join:
            for j in join:
                statement = statement.join(j)

        if options:
            statement = statement.options(*options)

        statement = statement.filter(*filters)
        result = await self.execute(statement)

        return result.unique().scalar_one_or_none()

    async def list(self, options=None, orders=None, joins=None, **kwargs) -> list[ModelType]:
        filters = self.parse_filters(model=self.model, **kwargs)
        statement = select(self.model)

        if joins:
            statement = statement.join(*joins)

        if options:
            statement = statement.options(*options)

        if orders is not None:
            statement = statement.order_by(orders)

        statement = statement.filter(*filters)
        result = await self.execute(statement)

        return list(result.unique().scalars())

    async def exists(self, **kwargs) -> bool:
        filters = self.parse_filters(model=self.model, **kwargs)
        query = select(exists().select_from(self.model).where(*filters))
        return await self.session.scalar(query)

    async def get(self, ident: Any | tuple[Any, ...], *args, **kwargs) -> ModelType | None:
        return await self.session.get(self.model, ident, *args, **kwargs)

    async def execute(self, *args, **kwargs):
        return await self.session.execute(*args, **kwargs)

    async def merge(self, *args, **kwargs):
        return await self.session.merge(*args, **kwargs)

    async def delete(self, **kwargs) -> None:
        filters = self.parse_filters(model=self.model, **kwargs)
        stmt = delete(self.model).filter(*filters)
        await self.execute(stmt)
