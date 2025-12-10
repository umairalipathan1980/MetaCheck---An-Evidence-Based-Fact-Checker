from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parents[2]


class AppSettings(BaseSettings):
    """Environment-driven application settings."""

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    google_fact_check_api_key: str | None = Field(None, env="GOOGLE_FACT_CHECK_API_KEY")
    wikipedia_access_token: str | None = Field(None, env="WIKIPEDIA_ACCESS_TOKEN")

    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        description="Origins allowed for CORS",
    )

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown keys to allow additional env vars


class HealthStatus(BaseModel):
    status: str = "ok"
    service: str = "metacheck-backend"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
