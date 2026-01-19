import os
from dataclasses import field

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.enums import ENVIRONMENT
from utils.misc import get_project_meta


class Config(BaseSettings):
    ENVIRONMENT: ENVIRONMENT
    API_STR: str = "/api"

    BACKEND_CORS_ORIGINS: list[str] = field(default_factory=lambda: ["*"])
    REQUEST_ID_HEADER_NAME: str = "X-Request-Id"

    # noinspection PyNestedDecorators
    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    APP_HOST: str
    APP_PORT: int

    @property
    def project_root_path(self):
        project_root_path = os.path.dirname(os.path.realpath(__file__))

        # Set the path as an environment variable so other parts of the code can access it
        # This avoids circular imports by not relying on the Config class
        os.environ["PROJECT_ROOT_PATH"] = project_root_path
        return project_root_path

    @property
    def project_meta(self):
        return get_project_meta("pyproject.toml")

    model_config = SettingsConfigDict(case_sensitive=True)
