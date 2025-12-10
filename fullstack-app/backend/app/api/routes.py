import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.settings import HealthStatus, get_settings
from app.services.metacheck_service import CONFIG_PATH, FinalAssessment, run_verification

router = APIRouter(prefix="/api", tags=["metacheck"])


class VerifyRequest(BaseModel):
    text: str = Field(..., description="Input text containing one or more claims")
    verbose: bool = Field(False, description="Enable verbose MetaCheck console logging")
    mode: Literal["basic", "comprehensive"] = Field(
        "basic", description="basic for concise output (default), comprehensive for full detail"
    )


@router.get("/health", response_model=HealthStatus, tags=["health"])
async def health_check(settings=Depends(get_settings)) -> HealthStatus:  # noqa: B008
    return HealthStatus()


@router.get("/config/domain-categories")
async def get_domain_config() -> dict[str, Any]:
    """Expose the domain classification taxonomy to the frontend."""
    path = Path(CONFIG_PATH)
    if not path.exists():
        raise HTTPException(status_code=500, detail="Domain config not found")
    try:
        with path.open("r") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load domain config: {exc}") from exc


@router.post("/verify", response_model=FinalAssessment)
async def verify_claims_api(
    request: VerifyRequest,
    settings=Depends(get_settings),  # noqa: B008
) -> FinalAssessment:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be empty")

    # Configure OpenAI provider (standard only)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="OPENAI_API_KEY missing")
    os.environ["OPENAI_API_KEY"] = api_key
    # Clear Azure-related vars to avoid conflicts
    for var in [
        "AZURE_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "OPENAI_BASE_URL",
        "OPENAI_API_VERSION",
        "OPENAI_MODEL",
    ]:
        os.environ.pop(var, None)

    # Ensure optional env vars are set for MetaCheck internals
    if settings.google_fact_check_api_key:
        os.environ["GOOGLE_FACT_CHECK_API_KEY"] = settings.google_fact_check_api_key
    if settings.wikipedia_access_token:
        os.environ["WIKIPEDIA_ACCESS_TOKEN"] = settings.wikipedia_access_token

    try:
        return await run_verification(text, verbose=request.verbose, mode=request.mode)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc
