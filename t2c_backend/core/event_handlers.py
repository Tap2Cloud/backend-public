import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


async def _startup(app) -> None:
    pass


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
