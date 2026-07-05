from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "LingoFlow API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database — required, no default
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    SECRET_KEY: str  # required — generate with: openssl rand -hex 32
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    # OpenAI-compatible AI backend
    # Leave OPENAI_BASE_URL empty to use OpenAI.
    # Set to https://api.groq.com/openai/v1 for Groq (free tier).
    OPENAI_BASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Content ingestion — external API keys
    YOUTUBE_API_KEY: str = ""
    PODCAST_INDEX_KEY: str = ""
    PODCAST_INDEX_SECRET: str = ""

    # Admin endpoints — protect with a static pre-shared key
    # Generate with: openssl rand -hex 32
    ADMIN_API_KEY: str = ""


settings = Settings()  # type: ignore[call-arg]
