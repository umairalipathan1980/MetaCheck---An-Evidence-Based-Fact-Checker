import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load backend .env before importing MetaCheck (required for API keys)
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Set config path for MetaCheck domain classification (app/config/config.json)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"
os.environ.setdefault("METACHECK_CONFIG_PATH", str(CONFIG_PATH))

try:
    from app.core.MetaCheck import FinalAssessment, verify_claims  # type: ignore

    # Ensure forward references are resolved for FastAPI schema generation
    FinalAssessment.model_rebuild()
except Exception as exc:  # pragma: no cover - import-time failure surfaced to API
    raise ImportError(f"Failed to import MetaCheck core: {exc}") from exc


async def run_verification(text: str, verbose: bool = False) -> FinalAssessment:
    """
    Run the MetaCheck verification workflow.

    Args:
        text: Input text containing one or more claims.
        verbose: Whether to enable MetaCheck verbose console output.

    Returns:
        FinalAssessment containing claim results and metacognitive detail.
    """
    return await verify_claims(text, verbose=verbose)
