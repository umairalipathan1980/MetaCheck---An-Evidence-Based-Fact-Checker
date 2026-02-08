import json
import os
import sys
import importlib
from pathlib import Path
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.settings import HealthStatus, get_settings
from app.services.metacheck_service import CONFIG_PATH, FinalAssessment, run_verification, run_claim_extraction
from app.services.comparison_service import run_comparison_analysis
from app.core.constants import MAX_TEXT_LENGTH
from app.core.tool_settings import load_tool_settings, save_tool_settings

router = APIRouter(prefix="/api", tags=["metacheck"])


class ExtractRequest(BaseModel):
    text: str = Field(..., description="Input text containing one or more claims")
    mode: Literal["basic", "comprehensive"] = Field(
        "basic", description="basic for concise output (default), comprehensive for full detail"
    )


class VerifyRequest(BaseModel):
    text: str = Field(..., description="Input text containing one or more claims")
    mode: Literal["basic", "comprehensive"] = Field(
        "basic", description="basic for concise output (default), comprehensive for full detail"
    )
    selected_claim_indices: Optional[list[int]] = Field(
        None,
        description="Optional list of claim indices to verify (0-indexed). If not provided, all claims will be verified."
    )


class StudentClaim(BaseModel):
    claim: str
    verdict: str
    confidence: float
    sourcesCount: int
    timeSpent: int
    reasoning: str
    keySources: list[str]
    timestamp: str


class CompareRequest(BaseModel):
    student_claims: list[StudentClaim] = Field(..., description="Student's assessed claims")
    ai_result: FinalAssessment = Field(..., description="AI verification result")


class ModeSettingsPayload(BaseModel):
    max_claims_to_verify_per_run: int = Field(..., ge=1, le=5)
    max_claims_to_extract: int = Field(..., ge=1, le=10)


class PerformanceSettingsPayload(BaseModel):
    model_choice: str
    per_claim_timeout_seconds: float = Field(..., gt=0)


class ToolSettingsUpdateRequest(BaseModel):
    basic: ModeSettingsPayload
    comprehensive: ModeSettingsPayload
    performance_cost_controls: PerformanceSettingsPayload


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


@router.get("/config/settings")
async def get_tool_settings_config(settings=Depends(get_settings)) -> dict[str, Any]:  # noqa: B008
    """Expose tool settings for the frontend Settings tab."""
    file_settings = load_tool_settings()
    perf = file_settings.get("performance_cost_controls", {})
    allowed_models = perf.get("allowed_models", ["gpt-5.1", "gpt-4.1-mini", "gpt-5-mini"])
    basic = file_settings.get("verification_scope", {}).get("basic", {})
    comprehensive = file_settings.get("verification_scope", {}).get("comprehensive", {})
    timeout_seconds = perf.get("per_claim_timeout_seconds", 90)
    model_choice = perf.get("model_choice", settings.open_ai_model)

    return {
        "ranges": {
            "max_claims_to_verify_per_run": "1-5",
            "max_claims_to_extract": "1-10",
        },
        "basic": {
            "max_claims_to_verify_per_run": int(basic.get("max_claims_to_verify_per_run", 5)),
            "max_claims_to_extract": int(basic.get("max_claims_to_extract", 10)),
            "model_choice_current": model_choice,
            "model_choices": allowed_models,
            "per_claim_timeout_seconds": timeout_seconds,
        },
        "comprehensive": {
            "max_claims_to_verify_per_run": int(comprehensive.get("max_claims_to_verify_per_run", 5)),
            "max_claims_to_extract": int(comprehensive.get("max_claims_to_extract", 10)),
            "model_choice_current": model_choice,
            "model_choices": allowed_models,
            "per_claim_timeout_seconds": timeout_seconds,
        },
    }


@router.put("/config/settings")
async def update_tool_settings_config(
    request: ToolSettingsUpdateRequest,
    settings=Depends(get_settings),  # noqa: B008
) -> dict[str, Any]:
    """Persist tool settings in app/config/settings.json."""
    print(f"[SAVE] Received settings update request:")
    print(f"[SAVE] Basic: max_claims_to_verify={request.basic.max_claims_to_verify_per_run}, "
          f"max_claims_to_extract={request.basic.max_claims_to_extract}")
    print(f"[SAVE] Comprehensive: max_claims_to_verify={request.comprehensive.max_claims_to_verify_per_run}, "
          f"max_claims_to_extract={request.comprehensive.max_claims_to_extract}")
    print(f"[SAVE] Performance: model={request.performance_cost_controls.model_choice}, "
          f"timeout={request.performance_cost_controls.per_claim_timeout_seconds}")

    current = load_tool_settings()
    allowed_models = current.get("performance_cost_controls", {}).get(
        "allowed_models",
        ["gpt-5.1", "gpt-4.1-mini", "gpt-5-mini"],
    )
    if request.performance_cost_controls.model_choice not in allowed_models:
        raise HTTPException(
            status_code=422,
            detail=f"model_choice must be one of: {', '.join(allowed_models)}",
        )

    payload = {
        "verification_scope": {
            "basic": request.basic.model_dump(),
            "comprehensive": request.comprehensive.model_dump(),
        },
        "performance_cost_controls": {
            "model_choice": request.performance_cost_controls.model_choice,
            "allowed_models": allowed_models,
            "per_claim_timeout_seconds": request.performance_cost_controls.per_claim_timeout_seconds,
        },
    }
    print(f"[SAVE] Payload to save: {json.dumps(payload, indent=2)}")
    try:
        saved = save_tool_settings(payload)
        print(f"[SAVE] Successfully saved settings: {json.dumps(saved, indent=2)}")
    except ValueError as exc:
        print(f"[SAVE] Validation error: {exc}")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        print(f"[SAVE] Save failed: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {exc}") from exc

    # Return refreshed view model used by frontend.
    return await get_tool_settings_config(settings=settings)


@router.post("/admin/reload-settings")
async def reload_settings() -> dict[str, Any]:
    """Reload settings modules to apply updated configuration without full restart."""
    try:
        print("[RELOAD] Starting settings reload...")

        # Clear the cached settings first
        if "app.core.settings" in sys.modules:
            from app.core.settings import get_settings
            get_settings.cache_clear()
            print("[RELOAD] Cleared get_settings() cache")

        # Reload modules in dependency order to ensure all cached values are updated
        modules_to_reload = [
            "app.core.tool_settings",      # Base settings loader
            "app.core.settings",           # Uses tool_settings, has cached get_settings()
            "app.core.constants",          # Uses tool_settings and settings
            "app.core.agents",             # Uses constants
            "app.core.workflow",           # Uses agents and constants
            "app.services.metacheck_service",  # Uses agents
            "app.services.comparison_service",  # Uses agents
        ]

        reloaded = []
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                print(f"[RELOAD] Reloading {module_name}")
                importlib.reload(sys.modules[module_name])
                reloaded.append(module_name)
            else:
                print(f"[RELOAD] Skipping {module_name} (not loaded)")

        # Verify reload by checking current values
        from app.core.constants import MAX_CLAIMS_BASIC, MAX_CLAIMS_COMPREHENSIVE, PER_CLAIM_TIMEOUT_SECONDS, MODEL_NAME
        from app.core.settings import get_settings
        current_settings = get_settings()
        print(f"[RELOAD] Current settings: MAX_CLAIMS_BASIC={MAX_CLAIMS_BASIC}, "
              f"MAX_CLAIMS_COMPREHENSIVE={MAX_CLAIMS_COMPREHENSIVE}, "
              f"PER_CLAIM_TIMEOUT_SECONDS={PER_CLAIM_TIMEOUT_SECONDS}")
        print(f"[RELOAD] Current MODEL_NAME from constants: {MODEL_NAME}")
        print(f"[RELOAD] Current model from get_settings(): {current_settings.open_ai_model}")

        return {
            "status": "success",
            "message": "Settings reloaded successfully",
            "reloaded_modules": reloaded
        }
    except Exception as exc:
        print(f"[RELOAD] Error: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload settings: {exc}"
        ) from exc


@router.post("/extract")
async def extract_claims_api(
    request: ExtractRequest,
    settings=Depends(get_settings),  # noqa: B008
) -> dict:
    """Extract claims from text without verifying them"""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be empty")

    # Validate text length
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters"
        )

    # Configure OpenAI provider (standard only)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="OPENAI_API_KEY missing")
    os.environ["OPENAI_API_KEY"] = api_key

    try:
        claim_list = await run_claim_extraction(text, mode=request.mode)

        file_settings = load_tool_settings()
        max_claims = int(
            file_settings["verification_scope"][request.mode]["max_claims_to_verify_per_run"]
        )

        return {
            "claims": [{"text": c.text, "worthiness_score": c.worthiness_score} for c in claim_list.claims],
            "total_extracted": len(claim_list.claims),
            "max_verifiable": max_claims,
            "mode": request.mode,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Claim extraction failed: {exc}") from exc


@router.post("/verify", response_model=FinalAssessment)
async def verify_claims_api(
    request: VerifyRequest,
    settings=Depends(get_settings),  # noqa: B008
) -> FinalAssessment:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be empty")

    # Validate text length
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters"
        )

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
        # Validate selected claim indices if provided
        if request.selected_claim_indices is not None:
            file_settings = load_tool_settings()
            max_claims = int(
                file_settings["verification_scope"][request.mode]["max_claims_to_verify_per_run"]
            )
            if len(request.selected_claim_indices) > max_claims:
                raise HTTPException(
                    status_code=422,
                    detail=f"Cannot verify more than {max_claims} claims in {request.mode} mode"
                )

        return await run_verification(
            text,
            mode=request.mode,
            selected_claim_indices=request.selected_claim_indices
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc


@router.post("/compare")
async def compare_analysis_api(
    request: CompareRequest,
    settings=Depends(get_settings),  # noqa: B008
) -> dict:
    """Analyze comparison between student claims and AI results"""
    if not request.student_claims:
        raise HTTPException(status_code=422, detail="Student claims cannot be empty")

    if not request.ai_result or not request.ai_result.claim_results:
        raise HTTPException(status_code=422, detail="AI results cannot be empty")

    try:
        result = await run_comparison_analysis(request.student_claims, request.ai_result)
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Comparison analysis failed: {exc}") from exc
