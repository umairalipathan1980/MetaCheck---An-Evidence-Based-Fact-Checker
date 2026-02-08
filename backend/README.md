# MetaCheck Backend (FastAPI)

FastAPI service exposing MetaCheck's verification workflow for the React frontend.

## Modular Architecture

The core engine has been refactored into focused modules for better maintainability:

```
app/core/
├── __init__.py      # Public API: verify_claims, FinalAssessment
├── MetaCheck.py     # Facade (backward compatible re-exports)
├── models.py        # 16 Pydantic models (Claim, Evidence, FinalAssessment, etc.)
├── constants.py     # VERDICT_CRITERIA, METACOGNITIVE_INSTRUCTIONS, MODEL_NAME
├── clients.py       # GoogleFactCheckClient, WikipediaClient + singleton instances
├── analysis.py      # MetacognitiveTracker
├── domain.py        # load_domain_config(), classify_web_source(), domain_classification_tool
├── tools.py         # wikipedia_search_tool, google_fact_check_tool
├── agents.py        # Agent definitions (claim_extractor, orchestrator)
├── workflow.py      # Main verify_claims() async function
└── settings.py      # Environment configuration (AppSettings)
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Readiness check |
| `/api/config/domain-categories` | GET | Domain credibility taxonomy (from `app/config/config.json`) |
| `/api/extract` | POST | Extract claims from text (no verification), returns claims with worthiness scores |
| `/api/verify` | POST | Fact-check text or selected claims, returns `FinalAssessment` |
| `/api/compare` | POST | Compare student claims with AI results, returns concise feedback (single LLM call) |
| `/api/settings/tool` | GET | Get current tool settings (verification scope, performance controls) |
| `/api/settings/tool` | PUT | Update tool settings with automatic backend reload |
| `/api/settings/reload` | POST | Manually reload backend modules after settings change |

**POST /api/extract** body:
```json
{
  "text": "string (required, max 2,000 chars)",
  "mode": "basic | comprehensive (optional, default: basic)"
}
```

**Response:**
```json
{
  "claims": [{"text": "...", "worthiness_score": 0.85}],
  "total_extracted": 5,
  "max_verifiable": 5,
  "mode": "basic"
}
```

**POST /api/verify** body:
```json
{
  "text": "string (required, max 2,000 chars)",
  "mode": "basic | comprehensive (optional, default: basic)",
  "selected_claim_indices": "array of integers (optional, 0-indexed)"
}
```

**Claim Count Limits:**
- Basic mode: Maximum 5 claims can be verified (configurable via settings)
- Comprehensive mode: Maximum 3 claims can be verified (configurable via settings)

## Configurable Settings

Settings are stored in `app/config/settings.json` and can be modified via the Settings UI (frontend) or directly edited.

**Verification Scope (per mode):**
- `max_claims_to_verify_per_run`: Maximum claims per verification request
- `max_claims_to_extract`: Maximum claims to extract from text
- `max_web_sources`: Maximum Tavily web search results per claim (1-5)
- `max_wikipedia_sources`: Maximum Wikipedia results per claim (1-5)
- `max_fact_check_sources`: Maximum Google Fact Check results per claim (1-5)

**Performance/Cost Controls:**
- `model_choice`: AI model (gpt-5.1, gpt-4.1-mini, gpt-5-mini)
- `per_claim_timeout_seconds`: Timeout for each claim verification
- `tavily_search_depth`: Tavily API mode ("basic" or "advanced")

**Module Reload System:**
When settings are saved via `/api/settings/tool` PUT endpoint, the backend automatically reloads affected modules:
- `app.core.tool_settings` → `app.core.settings` → `app.core.constants` → `app.core.tools` → `app.core.agents` → `app.core.workflow` → services

This enables runtime configuration changes without server restart.

## Setup

1. `cd backend`

2. Create `.env` (see `.env.example`):
   - `OPENAI_API_KEY` (required)
   - `GOOGLE_FACT_CHECK_API_KEY` (optional - enables fact-check database queries)
   - `WIKIPEDIA_ACCESS_TOKEN` (optional - Wikipedia works without auth)

3. Create venv & install deps:
   ```bash
   python -m venv .venv && .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

4. Run server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Usage

### Import Options

```python
# New minimal API (recommended)
from app.core import verify_claims, FinalAssessment

# Backward compatible import (all exports)
from app.core.MetaCheck import verify_claims, FinalAssessment

# Direct module imports (for advanced use)
from app.core.models import Claim, Evidence, VerificationResult
from app.core.clients import GoogleFactCheckClient, WikipediaClient
from app.core.analysis import MetacognitiveTracker
from app.core.domain import classify_web_source, load_domain_config
from app.core.agents import claim_extractor, orchestrator
```

### Run Verification

```python
import asyncio
from app.core import verify_claims

async def main():
    result = await verify_claims(
        "Donald Trump increased military recruitment in 2025.",
        mode="comprehensive"  # or "basic"
    )
    print(f"Claims: {result.total_claims}")
    for claim_result in result.claim_results:
        print(f"  {claim_result.verdict}: {claim_result.claim}")

asyncio.run(main())
```

## Agentic Workflow (Detailed)

### Step 1: Claim Extraction

```
INPUT TEXT → claim_extractor agent → ClaimList
```

**Agent:** `claim_extractor` (defined in `agents.py`)
**Instructions:** `EXTRACTION_INSTRUCTIONS` in `constants.py`

**Process:**
1. Receives raw input text
2. Identifies verifiable, falsifiable claims
3. Filters out opinions, common knowledge, vague statements
4. **Splits compound claims** (e.g., "Tower is 330m tall and attracts 7M visitors" → 2 claims)
5. Returns `ClaimList` with extracted claims

### Step 2: Parallel Orchestrator Per Claim

```
For each claim (max 5 parallel):
  orchestrator agent
    ├── Calls WebSearchTool (OpenAI hosted)
    ├── Calls domain_classification_tool (for each web result URL)
    ├── Calls wikipedia_search_tool
    ├── Calls google_fact_check_tool
    └── Synthesizes ALL evidence → VerificationResult
```

**Agent:** `orchestrator` (defined in `agents.py`)
**Instructions:** `VERDICT_CRITERIA` + `METACOGNITIVE_INSTRUCTIONS` in `constants.py`
**File:** `workflow.py:214-293` (`analyze_claim()` function)

**Evidence Gathering:**

| Tool | Purpose | Credibility |
|------|---------|-------------|
| `WebSearchTool()` | Real-time web search via OpenAI | Varies by domain (0.50-0.85) |
| `domain_classification_tool` | Classifies URL credibility by domain | Returns category + score |
| `wikipedia_search_tool` | Wikipedia API search + summaries | Fixed 0.8 |
| `google_fact_check_tool` | Professional fact-checker verdicts | Fixed 0.95 |

**Verdict Synthesis:**

The orchestrator applies `VERDICT_CRITERIA` to determine verdict:

| Verdict | Criteria |
|---------|----------|
| `SUPPORTED` | Multiple credible sources (≥0.7) confirm; no contradictions |
| `REFUTED` | Credible sources (≥0.7) explicitly contradict |
| `INSUFFICIENT_INFORMATION` | <2 sources OR all sources <0.7 credibility |
| `CONFLICTING_EVIDENCE` | Credible sources on BOTH sides disagree |

**Concurrency Model:**
```python
semaphore = asyncio.Semaphore(5)  # Max 5 claims running concurrently
# Configurable via METACHECK_MAX_CONCURRENCY env var

async def analyze_claim(claim_text):
    async with semaphore:
        # Run orchestrator (tools called sequentially by agent)
        agent_result = await Runner.run(orchestrator, ...)
        return VerificationResult

# All claims in parallel (or selected subset via selected_claim_indices)
claim_tasks = [analyze_claim(claim.text) for claim in claims]
results = await asyncio.gather(*claim_tasks)
```

**Two-Step Workflow Support:**

MetaCheck supports two modes of operation:

1. **Direct verification** (legacy): Submit text, all extracted claims are automatically verified
2. **Two-step workflow** (recommended):
   - Step 1: Call `/api/extract` to get claims with worthiness scores
   - Step 2: User selects claims, call `/api/verify` with `selected_claim_indices` parameter
   - Benefits: User control, cost savings, handles large texts gracefully

### Step 3: Result Aggregation

```
Collect all VerificationResults
  ├── Aggregate search statuses (success/error/no_results/no_api_key)
  ├── Calculate overall confidence (average across claims)
  └── Build FinalAssessment
```

**Output:** `FinalAssessment` with:
- `claim_results`: List of `VerificationResult` objects
- `search_status`: Aggregated `SearchStatusSummary`
- `overall_credibility`: Average confidence score
- `mode`: "basic" or "comprehensive"

## Module Descriptions

| Module | Purpose |
|--------|---------|
| `models.py` | All Pydantic data models (Claim, Evidence, FinalAssessment, MetacognitiveDetail, SearchStatus, etc.) |
| `constants.py` | Verdict criteria rules, metacognitive instructions, extraction instructions (including compound claim splitting), MODEL_NAME, text/claim limits (MAX_TEXT_LENGTH=2000, MAX_CLAIMS_BASIC=5, MAX_CLAIMS_COMPREHENSIVE=5) |
| `clients.py` | API clients for Google Fact Check and Wikipedia with singleton instances (lazy API key loading) |
| `analysis.py` | MetacognitiveTracker (reasoning steps, contradiction detection) |
| `domain.py` | Config-driven domain credibility classification (0.50-0.85 score range) |
| `tools.py` | Function tools for agents: `wikipedia_search_tool`, `google_fact_check_tool` (with status tracking) |
| `agents.py` | Agent definitions: `claim_extractor`, `orchestrator` (with ALL tools) |
| `services/comparison_service.py` | Comparison analysis via direct LLM call (concise feedback: summary + improvements) |
| `workflow.py` | Main `verify_claims()` async function with parallel orchestrators, search status tracking, and claim filtering support |

## Search Status Tracking

Every verification includes detailed status tracking for evidence gathering operations:

**Tracked Searches:**
- Wikipedia API (`wikipedia_search_tool`)
- Google Fact Check API (`google_fact_check_tool`)
- Web Search (via OpenAI agents library)

**Status Types:**
- `success` - Search completed successfully with results
- `no_results` - Search worked but found no relevant evidence
- `error` - Search failed due to API error or exception
- `no_api_key` - API key not configured (Google Fact Check only)

**Implementation:**
- `tools.py`: Global status tracking via `get_last_wikipedia_status()` and `get_last_google_fact_check_status()`
- `workflow.py`: Collects statuses after orchestrator runs, creates `SearchStatusSummary`
- `models.py`: `SearchStatus` and `SearchStatusSummary` models
- `clients.py`: Each client returns `(evidence_list, status)` tuple

**API Response:**
```json
{
  "input_text": "...",
  "claim_results": [...],
  "search_status": {
    "web_search": {"tool": "web_search", "status": "success", "results_count": 3},
    "wikipedia": {"tool": "wikipedia", "status": "success", "results_count": 2},
    "google_fact_check": {"tool": "google_fact_check", "status": "no_api_key", "results_count": 0}
  }
}
```

This helps distinguish between "no evidence found" (legitimate outcome) vs "search failed" (configuration/API issue).

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test imports
python -c "from app.core import verify_claims, FinalAssessment; print('OK')"
```

## Notes

- Domain config lives at `app/config/config.json`; `METACHECK_CONFIG_PATH` env var can override
- Frontend uses `VITE_API_URL` (defaults to `http://localhost:8000`)
- Requests can take 30-120s; frontend timeout is 120s
- Basic mode: concise output; Comprehensive mode: full metacognitive detail

