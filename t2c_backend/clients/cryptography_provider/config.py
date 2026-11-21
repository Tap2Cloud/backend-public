import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    CRYPTOGRAPHY_KEY: str = secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(case_sensitive=True)
