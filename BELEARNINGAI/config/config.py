"""Application configuration settings using Pydantic Settings."""

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
    # Database Configuration
    # mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")

    mongodb_url: str = Field(alias="MONGODB_URL")
    mongodb_database: str = Field(default="ai_learning_app", alias="MONGODB_DATABASE")
    
    # JWT Authentication Settings
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")

    # Thời gian hiệu lực của Access Token và Refresh Token
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # AI Services (Google GenAI / Gemini)
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-pro", alias="GEMINI_MODEL")
    
    # Redis Cache (Optional)
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", alias="REDIS_URL")


    # CORS Settings
    frontend_ip: Optional[str] = Field(default=None, alias="FRONTEND_IP")
    frontend_ports: List[int] = Field(default=[3000, 5173, 8081], alias="FRONTEND_PORTS")

    @property
    def allowed_origins(self) -> List[str]:
        """Dynamically construct the list of allowed CORS origins."""
        origins = {
            # Standard local development origins
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5500",  # For VSCode Live Server
        }

        if self.frontend_ip:
            # Add origins for the specified frontend IP and ports
            for port in self.frontend_ports:
                origins.add(f"http://{self.frontend_ip}:{port}")
            # Also add the IP without a port for standard HTTP/HTTPS access
            origins.add(f"http://{self.frontend_ip}")
            origins.add(f"https://{self.frontend_ip}")

        return sorted(list(origins))


    # Email Service
    sendgrid_api_key: Optional[str] = Field(default=None, alias="SENDGRID_API_KEY")
    from_email: str = Field(default="noreply@ailearning.com", alias="FROM_EMAIL")
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: Optional[int] = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    
    # File Storage
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    max_upload_size_mb: int = Field(default=50, alias="MAX_UPLOAD_SIZE_MB")
    s3_access_key_id: Optional[str] = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: Optional[str] = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    s3_bucket_name: Optional[str] = Field(default=None, alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="auto", alias="S3_REGION")
    s3_endpoint_url: Optional[str] = Field(default=None, alias="S3_ENDPOINT_URL")
    
    # Security Settings
    rate_limit_per_minute: int = Field(default=100, alias="RATE_LIMIT_PER_MINUTE")
    bcrypt_rounds: int = Field(default=12, alias="BCRYPT_ROUNDS")
    
    # Logging & Monitoring
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    
    # Feature Flags
    enable_ai_chat: bool = Field(default=True, alias="ENABLE_AI_CHAT")
    enable_email_notifications: bool = Field(default=True, alias="ENABLE_EMAIL_NOTIFICATIONS")
    enable_vector_search: bool = Field(default=False, alias="ENABLE_VECTOR_SEARCH")

    def get_allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string to list."""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


