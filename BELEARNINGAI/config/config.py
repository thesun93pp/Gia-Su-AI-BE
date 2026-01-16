from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = Field(default="AI Learning Platform API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    testing: bool = Field(default=False, alias="TESTING")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database Configuration
    mongodb_url: str = Field(alias="MONGODB_URL")
    mongodb_database: str = Field(default="ai_learning_app", alias="MONGODB_DATABASE")

    # JWT Authentication Settings
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # AI Services
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-pro", alias="GEMINI_MODEL")

    # Redis
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="ALLOWED_ORIGINS"
    )

    def get_allowed_origins_list(self) -> List[str]:
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins


@lru_cache()
def get_settings() -> Settings:
    return Settings()
