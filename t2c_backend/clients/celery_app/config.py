from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    CELERY_BROKER_URL: str = "amqp://user:root@localhost:5672"
    RESULT_BACKEND: str = Field("rpc://", alias="CELERY_RESULT_BACKEND")

    model_config = SettingsConfigDict(case_sensitive=True)
