from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='FASTAPI_',
        env_file=('.env', '.env.dev'),
        env_file_encoding='utf-8',
        env_nested_delimiter='_',
        extra='ignore',
    )

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG: bool = True

    ALLOW_ORIGINS: list[str] = []

    TELEGRAM_TOKEN: str
    TELEGRAM_ADMIN_CHAT_ID: int

    DOMAIN: HttpUrl

    GITHUB_WEBHOOK_SECRET: str


settings = Settings()  # type: ignore
