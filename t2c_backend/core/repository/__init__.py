import enum
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import (
    BigInteger,
    Column,
    ColumnElement,
    Text,
    and_,
    cast,
    delete,
    exists,
    func,
    literal,
    not_,
    or_,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.util import AliasedClass

from t2c_backend.core.db import AdvancedDeclarativeBase

ModelType = TypeVar("ModelType", bound=AdvancedDeclarativeBase)


class TableLockMode(enum.StrEnum):
    """
    The Postgres table lock modes worth taking from application code.

    What separates them is which other transactions may still read, and whether two
    transactions can hold the mode at the same time. The full conflict matrix lives in the
    Postgres docs under "Explicit Locking".
    """

    # Blocks writers, but is shared: two transactions can hold it at once and then deadlock
    # the moment they both try to write. Safe only when nothing writes afterwards.
    SHARE = "SHARE"
    # Blocks writers and is self exclusive, so a read-then-write pair cannot interleave with
    # another request's. Plain SELECT is unaffected.
    EXCLUSIVE = "EXCLUSIVE"
    # Blocks everything, readers included. Only needed for schema level work.
    ACCESS_EXCLUSIVE = "ACCESS EXCLUSIVE"

    def __str__(self) -> str:
        return self.value


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

    async def lock_table(self, mode: TableLockMode = TableLockMode.EXCLUSIVE) -> None:
        """
        Take a table lock that Postgres releases when the request commits or rolls back.

        The default EXCLUSIVE mode keeps plain SELECT running and blocks every writer, which is
        what a read-then-write check needs: ask "does this value already exist?", then write if
        it does not. Without the lock two concurrent requests both read "no", both write, and
        both commit. A unique index is the cheaper guard when one can be added; this is the
        fallback when it cannot, and the only guard that covers a value which does not exist
        yet, since a row lock has no row to attach to.

        Postgres locks tables and rows, never columns, so this covers the whole table and
        serialises every writer of it for the rest of the request. Prefer lock_values() when
        the guard only needs to cover one combination of values; reach for this when the whole
        table genuinely has to hold still.
        """
        # A lock belongs to the transaction that took it, and the reader and writer engines are
        # separate connections running separate transactions. Routed by statement type this
        # would land on the reader, leaving the writer's INSERT waiting on a lock held by its
        # own request, which nothing can release. So pin the session to the writer that will
        # run the save, the same way save() below does.
        self.session.info["engine"] = "writer"
        await self.session.execute(
            text(f"LOCK TABLE {self.model.__table__.fullname} IN {mode} MODE")
        )

    async def lock_values(self, **kwargs: Any) -> None:
        """
        Take a lock on one combination of column values, released on commit or rollback.

        Narrower than lock_table(): it holds up only the requests competing for the same values
        and leaves every other writer of the table running. Use it to make a read-then-write
        check atomic - "is this name taken?", then insert - which is exactly the case a row
        lock cannot cover, because the row being guarded against does not exist yet.

        Postgres keys these locks by number, so the values are hashed rather than compared and
        are matched exactly. Pass a SQL expression for anything the check compares loosely -
        func.lower(name) next to an ilike check - so that the key folds the value the same way
        the check does. Do not fold it in Python first: Python and Postgres disagree on some
        Unicode (Turkish dotted I, Greek final sigma), which would hand two names the check
        calls equal two different keys, and the guard would silently do nothing for them. The
        hashing happens in Postgres for the same reason.

        Unrelated values can in principle hash to the same key; that costs a little contention,
        never correctness.
        """
        # Every part is cast to text: Postgres has to be told the type of a bare parameter, and
        # it also keeps 1 and "1" from hashing alike. The table name keeps two models from
        # sharing a key, and sorting keeps the key stable regardless of the order the caller
        # passed the values in.
        parts = [cast(literal(self.model.__table__.fullname), Text)]
        for column in sorted(kwargs):
            value = kwargs[column]
            expression = value if isinstance(value, ColumnElement) else literal(value)
            parts.append(
                cast(literal(f"{column}="), Text)
                + func.coalesce(cast(expression, Text), cast(literal("\x1e<null>"), Text))
            )

        # A unit separator cannot appear in a normalised name, so no two different sets of
        # values can be glued into the same payload.
        payload = func.concat_ws(cast(literal("\x1f"), Text), *parts)

        # The lock belongs to the connection that took it, and the reader and writer engines
        # hold separate ones, so pin the session to the writer that will run the save.
        self.session.info["engine"] = "writer"
        await self.session.execute(
            select(
                func.pg_advisory_xact_lock(
                    func.hashtextextended(payload, cast(literal(0), BigInteger))
                )
            )
        )

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
        where: list[ColumnElement] | None = None,
        **kwargs,
    ) -> ModelType:
        """
        The kwargs filters only reach columns of this repository's own model, since that is the
        only model parse_filters is given. Pass a condition on a joined model through `where`
        instead, alongside the `join` that brings it into the query - scoping a user to an
        organization, say, which lives on Location rather than on User.
        """
        filters = self.parse_filters(model=self.model, **kwargs)
        statement = select(self.model)

        if join:
            for j in join:
                statement = statement.join(j)

        if options:
            statement = statement.options(*options)

        if where:
            filters.extend(where)

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
