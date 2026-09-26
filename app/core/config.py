import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
