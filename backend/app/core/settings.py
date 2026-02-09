from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from app.core.tool_settings import load_tool_settings


BASE_DIR = Path(__file__).resolve().parents[2]
TOOL_SETTINGS = load_tool_settings()


class AppSettings(BaseSettings):
    """Environment-driven application settings."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    open_ai_model: str = Field(
        TOOL_SETTINGS["performance_cost_controls"]["model_choice"],
        env="OPEN_AI_MODEL",
        description="Default OpenAI model name for MetaCheck agents",
    )
    openai_transcription_model: str = Field(
        "whisper-1",
        env="OPENAI_TRANSCRIPTION_MODEL",
        description="OpenAI transcription model for audio processing",
    )

    # External API Keys
    google_fact_check_api_key: str | None = Field(None, env="GOOGLE_FACT_CHECK_API_KEY")
    wikipedia_access_token: str | None = Field(None, env="WIKIPEDIA_ACCESS_TOKEN")

    # Admin Authentication
    admin_username: str = Field(..., env="ADMIN_USERNAME")
    admin_password: str = Field(..., env="ADMIN_PASSWORD")
    user_username: str = Field("user", env="USER_USERNAME")
    user_password: str = Field("metacheck3.14", env="USER_PASSWORD")

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
