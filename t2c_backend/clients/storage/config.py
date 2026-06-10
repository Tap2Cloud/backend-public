from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    STORAGE_TYPE: Literal["DISK", "S3"]
    BUCKET: str

    model_config = SettingsConfigDict(case_sensitive=True)
