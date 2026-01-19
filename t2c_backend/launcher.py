import logging
import os.path
import sys

from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger
from loguru import logger
from main import app
from utils.enums import ENVIRONMENT

log_level_mapping = {
    ENVIRONMENT.DEVELOPMENT: logging.DEBUG,
    ENVIRONMENT.TEST: logging.DEBUG,
    ENVIRONMENT.PRODUCTION: logging.INFO,
    ENVIRONMENT.STAGING: logging.INFO,
}

LOG_LEVEL = log_level_mapping.get(app.config.ENVIRONMENT, logging.ERROR)


class InterceptHandler(logging.Handler):
    def emit(self, record) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg) -> None:
        self.loglevel = self.LOG_LEVELS.get(cfg.loglevel.lower(), logging.INFO)
        self.error_log = logging.getLogger("gunicorn.error")
        self.error_log.addHandler(logging.NullHandler())
        self.access_log = logging.getLogger("gunicorn.access")
        self.access_log.addHandler(logging.NullHandler())
        self.error_log.setLevel(self.loglevel)
        self.access_log.setLevel(self.loglevel)


class StandaloneApplication(BaseApplication):
    """Our Gunicorn application."""

    def __init__(self, application, options=None) -> None:
        self.options = options or {}
        self.application = application
        super().__init__()

    def load_config(self) -> None:
        for key, value in self.options.items():
            if key not in self.cfg.settings:
                raise ValueError(f"Unknown gunicorn option {key!r}")
            self.cfg.set(key, value)

    def load(self):
        return self.application


def setup_logging() -> None:
    # intercept everything at the root logger
    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    # configure loguru
    logger.configure(
        handlers=[{"sink": sys.stdout, "serialize": app.config.JSON_LOGS, "level": LOG_LEVEL}],
    )
    logger.add(os.path.join("logs", f"{app.config.PROJECT_NAME}.log"), rotation="500 MB")


if __name__ == "__main__":
    setup_logging()

    server_options = {
        "bind": f"{app.config.APP_HOST}:{app.config.APP_PORT}",
        "workers": app.config.GUNICORN_WORKERS,
        "timeout": 0,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    StandaloneApplication(app, server_options).run()
