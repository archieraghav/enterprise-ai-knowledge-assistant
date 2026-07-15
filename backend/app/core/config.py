from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Centralized application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Enterprise AI Knowledge Assistant"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "knowledge_assistant"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    s3_bucket_name: str = ""
    max_upload_size_mb: int = 25

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def load_settings() -> Settings:
    """Load settings, preferring AWS Secrets Manager in production environments."""
    base_settings = Settings()

    if base_settings.environment != "production":
        return base_settings

    from app.core.secrets import get_secret

    secret_data = get_secret("knowledge-assistant/prod")
    if secret_data is None:
        return base_settings

    return Settings(**{**base_settings.model_dump(), **secret_data})


settings = load_settings()