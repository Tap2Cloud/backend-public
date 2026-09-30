from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    EMAIL_PROVIDER_API_KEY: str
    SENDER_EMAIL: str
    VERIFICATION_EMAIL_TEMPLATE_ID: str

    model_config = SettingsConfigDict(case_sensitive=True)
