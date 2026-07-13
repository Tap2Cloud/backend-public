import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from t2c_backend.core.db import Engine
from t2c_backend.utils.enums import ENVIRONMENT

logger = logging.getLogger(__name__)


async def _startup(app) -> None:
    app.database_engine = Engine(
        app.config.DATABASE_NAME,
        app.config.DATABASE_USER,
        app.config.DATABASE_PASSWORD,
        app.config.DATABASE_HOST,
        app.config.DATABASE_PORT,
        echo=app.config.ENVIRONMENT != ENVIRONMENT.PRODUCTION,
    )

    # Bring up the waygate backend and start its background listeners. With the
    # Redis backend these keep rate-limit policies / route state in sync across
    # instances via pub/sub; with the in-memory backend the listeners exit
    # silently, so this is safe regardless of which backend is configured.
    await app.waygate_engine.backend.startup()
    await app.waygate_engine.start()


async def _shutdown(app) -> None:
    await app.waygate_engine.stop()
    await app.waygate_engine.backend.shutdown()


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    logger.info("Running app start handler.")
    await _startup(app)
    yield
    logger.info("Running app shutdown handler.")
    await _shutdown(app)
