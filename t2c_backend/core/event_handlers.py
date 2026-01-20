import logging
from collections.abc import Callable

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


async def _shutdown(app) -> None:
    pass


def start_app_handler(app) -> Callable:
    async def startup() -> None:
        logger.info("Running app start handler.")
        await _startup(app)

    return startup


def stop_app_handler(app) -> Callable:
    async def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        await _shutdown(app)

    return shutdown
