import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from agents import Runner

# Load backend .env before importing MetaCheck (required for API keys)
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Set config path for MetaCheck domain classification (app/config/config.json)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"
os.environ.setdefault("METACHECK_CONFIG_PATH", str(CONFIG_PATH))

try:
    from app.core.MetaCheck import FinalAssessment, verify_claims, ClaimList  # type: ignore
    from app.core.agents import claim_extractor
    from app.core.tool_settings import load_tool_settings

    # Ensure forward references are resolved for FastAPI schema generation
    FinalAssessment.model_rebuild()
except Exception as exc:  # pragma: no cover - import-time failure surfaced to API
    raise ImportError(f"Failed to import MetaCheck core: {exc}") from exc


async def run_claim_extraction(text: str, mode: str = "basic") -> ClaimList:
    """
    Extract claims from text without verifying them.

    Args:
        text: Input text containing one or more claims.
        mode: "basic" or "comprehensive" (affects max claim limit).

    Returns:
        ClaimList containing extracted claims with worthiness scores.
    """
    # Run claim extraction
    extracted = await Runner.run(claim_extractor, text)
    claim_list = extracted.final_output if extracted else None

    if not claim_list or not claim_list.claims:
        return ClaimList(claims=[], extraction_method="AI claim extractor")

    file_settings = load_tool_settings()
    mode_settings = file_settings.get("verification_scope", {}).get(mode, {})
    max_extract = int(mode_settings.get("max_claims_to_extract", 10))
    claim_list.claims = claim_list.claims[:max_extract]
    return claim_list


async def run_verification(
    text: str,
    mode: str = "basic",
    selected_claim_indices: Optional[list[int]] = None,
    selected_claim_texts: Optional[list[str]] = None,
) -> FinalAssessment:
    """
    Run the MetaCheck verification workflow.

    Args:
        text: Input text containing one or more claims.
        mode: "basic" for concise output or "comprehensive" for full metacognitive detail.
        selected_claim_indices: Optional list of 0-indexed claim indices to verify.
        selected_claim_texts: Optional pre-extracted selected claim texts for direct verification.

    Returns:
        FinalAssessment containing claim results and metacognitive detail.
    """
    return await verify_claims(
        text,
        mode=mode,
        selected_claim_indices=selected_claim_indices,
        selected_claim_texts=selected_claim_texts,
    )
