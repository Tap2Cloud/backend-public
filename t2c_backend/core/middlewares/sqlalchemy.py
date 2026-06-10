from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
)
from starlette.types import Receive, Scope, Send

from t2c_backend.core.db.session import reset_session_context, set_session_context


class SQLAlchemyMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        session_id = request.headers.get(request.app.config.REQUEST_ID_HEADER_NAME)
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            raise e
        finally:
            if isinstance(request.app.database_engine.session, async_scoped_session):
                await request.app.database_engine.session.remove()
            elif isinstance(request.app.database_engine.session, AsyncSession):
                await request.app.database_engine.session.close()
            request.app.services.remove_session(session_id=session_id)
            reset_session_context(context=context)
