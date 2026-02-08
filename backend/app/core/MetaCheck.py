"""
MetaCheck - Metacognitive Information-Assessment Tool

"""

import os
import asyncio

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables.")

# Verify API keys are set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Please set it in .env file or as environment variable.")

if not os.getenv("GOOGLE_FACT_CHECK_API_KEY"):
    print("Warning: GOOGLE_FACT_CHECK_API_KEY not found. Fact-check database queries will be disabled.")

if not os.getenv("WIKIPEDIA_ACCESS_TOKEN"):
    print("Info: WIKIPEDIA_ACCESS_TOKEN not found. Wikipedia API will work without authentication.")


# ============================================================================
# RE-EXPORTS FOR BACKWARD COMPATIBILITY
# ============================================================================

# Re-export all models
from app.core.models import (
    Claim,
    ClaimList,
    Evidence,
    MetacognitiveStep,
    VerificationResult,
    FinalAssessment,
    ContradictionDetection,
    SearchQuery,
    DomainClassification,
    SourceAssessment,
    VerdictReasoning,
    RejectedSource,
    MetacognitiveDetail,
    OrchestratorOutput,
    SearchStatus,
    SearchStatusSummary,
)

# Re-export constants
from app.core.constants import (
    VERDICT_CRITERIA,
    METACOGNITIVE_INSTRUCTIONS,
    EXTRACTION_INSTRUCTIONS,
    MODEL_NAME,
)

# Re-export clients
from app.core.clients import (
    GoogleFactCheckClient,
    WikipediaClient,
    google_fact_check_client,
    wikipedia_client,
)

# Re-export analysis classes
from app.core.analysis import (
    MetacognitiveTracker,
)

# Re-export domain classification
from app.core.domain import (
    load_domain_config,
    classify_web_source,
    domain_classification_tool,
)

# Re-export tools
from app.core.tools import (
    wikipedia_search_tool,
    google_fact_check_tool,
)

# Re-export agents
from app.core.agents import (
    claim_extractor,
    orchestrator,
)

# Re-export main workflow
from app.core.workflow import verify_claims

# Legacy alias for extraction_instructions
extraction_instructions = EXTRACTION_INSTRUCTIONS


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    asyncio.run(main())
