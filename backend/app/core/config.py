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
    tesseract_cmd_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    enable_cloudwatch_logging: bool = False
    use_secrets_manager: bool = False
    cloudwatch_log_group: str = "knowledge-assistant"
    cloudwatch_log_stream: str = "backend"
    rate_limit_per_minute: int = 60
    cors_allowed_origins_raw: str = '["http://localhost:5173"]'

    @property
    def cors_allowed_origins(self) -> list[str]:
        import json
        try:
            return json.loads(self.cors_allowed_origins_raw)
        except json.JSONDecodeError:
            return [origin.strip() for origin in self.cors_allowed_origins_raw.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def load_settings() -> Settings:
    """Load settings, optionally overlaying AWS Secrets Manager values.

    Secrets Manager is only consulted if USE_SECRETS_MANAGER=true is
    explicitly set — this keeps simple deployments (env vars only, e.g.
    Render, Railway) working without requiring AWS credentials.
    """
    base_settings = Settings()

    if not base_settings.use_secrets_manager:
        return base_settings

    from app.core.secrets import get_secret

    secret_data = get_secret("knowledge-assistant/prod")
    if secret_data is None:
        return base_settings

    return Settings(**{**base_settings.model_dump(), **secret_data})


settings = load_settings()