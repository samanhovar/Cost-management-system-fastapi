import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Add token's expire time
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 5   # 5 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = (60 * 60) * 24  # one day

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
