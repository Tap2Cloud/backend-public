import asyncio
import importlib.machinery
import importlib.util
import logging
import sys
import traceback
import types
from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from config import Config
from core.error_handlers import application_exception_handler
from core.event_handlers import start_app_handler, stop_app_handler
from core.middlewares.language import LanguageMiddleware
from core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from endpoints.router import api_router
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from utils.enums import ENVIRONMENT
from utils.errors import ApplicationError
from utils.misc import DictContainer, _is_submodule, maybe_coroutine, underscore

initial_clients = []


def get_middleware_stack(app_config):
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=app_config.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            CorrelationIdMiddleware,
            header_name=app_config.REQUEST_ID_HEADER_NAME,
            update_request_header=True,
            generator=lambda: uuid4().hex,
            validator=is_valid_uuid4,
            transformer=lambda a: a,
        ),
        Middleware(SQLAlchemyMiddleware),
        Middleware(LanguageMiddleware),
    ]


class CustomFastAPI(FastAPI):
    """
    Custom FastAPI class that encapsulates the app setup and configuration.
    """

    def __init__(self) -> None:
        # Initialize the parent FastAPI class
        self.config = Config()

        super().__init__(
            title=self.config.PROJECT_NAME,
            version=self.config.project_meta["version"],
            debug=self.config.ENVIRONMENT != ENVIRONMENT.PRODUCTION,
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            middleware=get_middleware_stack(self.config),
        )

        self.__extensions = {}
        self.services = DictContainer(package_type="Service", session_based=True)
        self.clients = DictContainer(package_type="Client")

        # Include routers
        self.include_router(api_router, prefix=self.config.API_STR)

        # Add exception handlers
        self.add_exception_handler(ApplicationError, application_exception_handler)

        # Add event handlers
        self.add_event_handler("startup", start_app_handler(self))
        self.add_event_handler("shutdown", stop_app_handler(self))

    async def setup_hook(self) -> None:
        for extension in initial_clients:
            try:
                await self.load_extension(extension)
                logging.info(f"Successfully loaded extension {extension}")
            except Exception as e:
                logging.warning(f"Failed to load extension {extension}: {e}")
                traceback.print_exc()

    def add_service(self, service, session_id):
        service_name = underscore(service.__class__.__name__)
        self.services.add_package(service_name, service, session_id)
        return service

    def add_client(self, client, client_name: str = None):
        client_name = underscore(client_name or client.__class__.__name__)
        existing = self.clients.get(client_name)

        if existing is not None:
            raise ValueError(f"Client {client_name} already exists.")

        self.clients[client_name] = client
        return client

    async def _call_module_finalizers(self, lib: types.ModuleType, key: str) -> None:
        try:
            func = getattr(lib, "teardown")
        except AttributeError:
            pass
        else:
            try:
                await maybe_coroutine(func, self)
            except Exception as e:
                logging.exception(f"Error during teardown of extension '{key}': {e}")
        finally:
            self.__extensions.pop(key, None)
            sys.modules.pop(key, None)
            name = lib.__name__
            for module in list(sys.modules.keys()):
                if _is_submodule(name, module):
                    del sys.modules[module]

    async def _load_from_module_spec(self, spec: importlib.machinery.ModuleSpec, key: str) -> None:
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)
        except Exception as e:
            del sys.modules[key]
            raise e

        try:
            setup = getattr(lib, "setup")
        except AttributeError as e:
            del sys.modules[key]
            raise e

        try:
            module = await maybe_coroutine(setup, self)
        except Exception as e:
            del sys.modules[key]
            await self._call_module_finalizers(lib, key)
            raise e
        else:
            self.__extensions[key] = lib
            return module

    def _resolve_name(self, name: str, package: str | None) -> str:
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError as e:
            raise e

    async def load_extension(self, name: str, *, package: str | None = None) -> None:
        name = self._resolve_name(name, package)
        if name in self.__extensions:
            raise ValueError("The service is already loaded.")

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ModuleNotFoundError(name)

        await self._load_from_module_spec(spec, name)

    @classmethod
    async def create(cls):
        instance = cls()
        await instance.setup_hook()
        return instance


app = asyncio.run(CustomFastAPI.create())
