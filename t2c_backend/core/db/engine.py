from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from t2c_backend.core.db.session import get_session_context, routing_session_class


class Engine:
    def __init__(
        self,
        database: str,
        username: str,
        password: str,
        host: str,
        port: int,
        echo: bool = True,
    ) -> None:
        self.url = URL.create(
            drivername="postgresql+asyncpg",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        ).render_as_string(hide_password=False)
        self.engines = {
            "writer": create_async_engine(
                self.url,
                pool_recycle=3600,
                echo=echo,
                echo_pool="debug",
                poolclass=NullPool,
            ),
            "reader": create_async_engine(
                self.url,
                pool_recycle=3600,
                echo=echo,
                echo_pool="debug",
                poolclass=NullPool,
            ),
        }
        self.async_session_factory = self.async_session_factory_creator(expire_on_commit=False)
        self.session = async_scoped_session(
            session_factory=self.async_session_factory,
            scopefunc=get_session_context,
        )

    def async_session_factory_creator(self, expire_on_commit=True):
        return async_sessionmaker(
            sync_session_class=routing_session_class(self.engines),
            expire_on_commit=expire_on_commit,
        )
