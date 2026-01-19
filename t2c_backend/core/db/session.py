import logging
from contextvars import ContextVar, Token

from fastapi import Request
from sqlalchemy import Delete, Insert, Update, exc
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


def routing_session_class(engines):
    class RoutingSession(Session):
        def get_bind(self, mapper=None, clause=None, **kw):
            if (
                self._flushing
                or self.info.get("engine") == "writer"
                or isinstance(clause, Update | Delete | Insert)
                or getattr(clause, "_for_update_arg", None) is not None
            ):
                return engines["writer"].sync_engine
            return engines["reader"].sync_engine

    return RoutingSession


async def get_db_session(request: Request):
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    async with request.app.database_engine.session(
        info={"session_id": request.headers[request.app.config.REQUEST_ID_HEADER_NAME]},
    ) as s:
        try:
            yield s
        except exc.SQLAlchemyError as error:
            logger.debug(f"Rolling back due to exception {error}.")
            await s.rollback()
            raise error
        else:
            await s.commit()
        finally:
            await s.close()
