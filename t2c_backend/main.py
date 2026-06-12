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
from fastapi import APIRouter, FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from t2c_backend.config import Config
from t2c_backend.core.error_handlers import application_exception_handler
from t2c_backend.core.event_handlers import lifespan
from t2c_backend.core.middlewares.language import LanguageMiddleware
from t2c_backend.core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from t2c_backend.endpoints.router import api_router
from t2c_backend.utils.enums import ENVIRONMENT
from t2c_backend.utils.errors import ApplicationError
from t2c_backend.utils.misc import DictContainer, _is_submodule, maybe_coroutine, underscore

initial_clients = [
    "t2c_backend.clients.token_backend",
    "t2c_backend.clients.cryptography",
    "t2c_backend.clients.storage",
]


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.config.PROJECT_NAME,
        version=app.config.project_meta["version"],
        routes=app.routes,
    )

    def fix_binary(node):
        if isinstance(node, dict):
            if (
                node.get("contentMediaType") == "application/octet-stream"
                and node.get("type") == "string"
            ):
                node.pop("contentMediaType", None)
                node["format"] = "binary"
            for v in node.values():
                fix_binary(v)
        elif isinstance(node, list):
            for v in node:
                fix_binary(v)

    fix_binary(schema)
    app.openapi_schema = schema
    return schema


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

    config_class = Config

    def get_api_router(self) -> APIRouter:
        """Return the router registered under API_STR. Override in subclasses
        to replace the route table instead of stacking a second one on top."""
        return api_router

    def __init__(self) -> None:
        # Initialize the parent FastAPI class
        self.config = self.config_class()

        super().__init__(
            title=self.config.PROJECT_NAME,
            version=self.config.project_meta["version"],
            debug=self.config.ENVIRONMENT != ENVIRONMENT.PRODUCTION,
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            middleware=get_middleware_stack(self.config),
            lifespan=lifespan,
        )

        self.__extensions = {}
        self.services = DictContainer(package_type="Service", session_based=True)
        self.clients = DictContainer(package_type="Client")

        # Include routers
        self.include_router(self.get_api_router(), prefix=self.config.API_STR)

        # Add exception handlers
        self.add_exception_handler(ApplicationError, application_exception_handler)

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
app.openapi = custom_openapi
