# MetaCheck

MetaCheck is an educational fact-checking tool that makes AI reasoning transparent. It:
- Extracts verifiable claims from text
- Searches web, Wikipedia, and fact-check APIs for evidence
- Classifies domain credibility via a configurable taxonomy
- Weighs evidence and issues structured verdicts with confidence
- Surfaces full metacognitive detail for students (search strategy, stance, uncertainties, assumptions, verdict reasoning)

Stack: FastAPI backend + React/Vite frontend (Tailwind + shadcn-style components) powered by a modular core engine. Uses standard OpenAI (`OPENAI_API_KEY`) plus optional Google Fact Check and Wikipedia keys.

Verdicts: `SUPPORTED`, `REFUTED`, `INSUFFICIENT_INFORMATION`, `CONFLICTING_EVIDENCE`.

## Architecture

```
fullstack-app/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── core/              # Core MetaCheck Engine (modular)
│   │   │   ├── __init__.py    # Public API: verify_claims, FinalAssessment
│   │   │   ├── MetaCheck.py   # Facade (backward compatible re-exports)
│   │   │   ├── models.py      # Pydantic data models
│   │   │   ├── constants.py   # Verdict criteria, instructions, config
│   │   │   ├── clients.py     # API clients (Google Fact Check, Wikipedia)
│   │   │   ├── analysis.py    # MetacognitiveTracker
│   │   │   ├── domain.py      # Domain classification logic
│   │   │   ├── tools.py       # Function tools for agents
│   │   │   ├── agents.py      # Agent definitions (orchestrator, extractors)
│   │   │   ├── workflow.py    # Main verify_claims function
│   │   │   └── settings.py    # Environment configuration
│   │   ├── config/
│   │   │   └── config.json    # Domain credibility taxonomy
│   │   ├── api/
│   │   │   └── routes.py      # FastAPI endpoints
│   │   └── services/
│   │       └── metacheck_service.py  # Service layer wrapper
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt
│
└── frontend/                   # React + Vite Frontend
    ├── src/
    │   ├── components/        # UI components
    │   ├── hooks/             # Custom hooks (useVerify)
    │   └── lib/               # API client, utilities
    └── package.json
```

## Agentic Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT TEXT (max 2,000 chars)                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 1: Claim Extraction Agent                    │
│               (claim_extractor)                                 │
│   • Extracts verifiable, falsifiable claims                     │
│   • Filters opinions and common knowledge                       │
│   • Splits compound claims into atomic statements               │
│   • Returns claims with worthiness scores                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            STEP 2: Claim Preview & Selection (UI)               │
│   • Display all extracted claims with worthiness scores         │
│   • Paginated view: 5 claims per page with prev/next buttons   │
│   • User selects which claims to verify (checkbox UI)           │
│   • Limits: 8 claims (basic mode) | 5 claims (comprehensive)   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
          ┌─────────┐      ┌─────────┐      ┌─────────┐
          │ Claim 1 │      │ Claim 2 │      │ Claim N │
          └─────────┘      └─────────┘      └─────────┘
                │                │                │
┌───────────────┴────────────────┴────────────────┴───────────────┐
│         STEP 3: Parallel Orchestrator Agents                    │
│         (One orchestrator per claim, max 5 concurrent)          │
│                                                                 │
│   Each orchestrator has ALL tools:                              │
│   ┌─────────────────┐ ┌──────────────┐ ┌────────────────┐     │
│   │  WebSearchTool  │ │  Wikipedia   │ │  Google Fact   │     │
│   │  (OpenAI)       │ │  Search      │ │  Check API     │     │
│   └────────┬────────┘ └──────┬───────┘ └───────┬────────┘     │
│            └──────────────────┼─────────────────┘              │
│                               ▼                                │
│                    ┌──────────────────────┐                    │
│                    │ domain_classification│                    │
│                    │       _tool          │                    │
│                    └──────────────────────┘                    │
│                                                                 │
│   Agent calls tools sequentially, sees ALL evidence,           │
│   applies VERDICT_CRITERIA, outputs VerificationResult         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: Aggregate & Return Results                 │
│              • Collect all VerificationResults                  │
│              • Aggregate search statuses                        │
│              • Calculate overall confidence                     │
│              • Return FinalAssessment                           │
└─────────────────────────────────────────────────────────────────┘
```

**Key Points:**
- **Text length limit**: 2,000 characters maximum
- **Claim count limits**: 5 for basic mode, 5 for comprehensive mode
- **Pagination**: 5 claims displayed per page with Previous/Next navigation
- **Two-step workflow**: Extract → Select → Verify (user control over which claims to verify)
- **Claims run in parallel** (bounded by semaphore, default: 5 concurrent)
- **Tools run sequentially** within each orchestrator (agent-controlled)
- **Orchestrator sees ALL evidence** before making verdict decision
- Verdicts: `SUPPORTED`, `REFUTED`, `INSUFFICIENT_INFORMATION`, `CONFLICTING_EVIDENCE`

## Main Components

- **Core Engine (`backend/app/core/`)**: Modular multi-agent orchestration system
  - `models.py`: 16 Pydantic models for claims, evidence, verdicts, metacognitive detail
  - `agents.py`: Agent definitions (claim_extractor, orchestrator)
  - `workflow.py`: Main `verify_claims()` async function
  - `domain.py`: Config-driven domain credibility classification
  - `analysis.py`: MetacognitiveTracker
  - `clients.py`: GoogleFactCheckClient, WikipediaClient

- **Domain Taxonomy (`backend/app/config/config.json`)**: Credibility scores and categories for domain classification (0.50-0.85 range)

- **Backend (`backend/`)**: FastAPI service exposing health, domain-config, and verification APIs

- **Frontend (`frontend/`)**: Student-facing UI for optional self-assessment, AI analysis, comparison, and documentation

## Search Status Tracking

MetaCheck now tracks the success/failure status of all evidence gathering operations. Each verification result includes a `search_status` object showing:

- **Status types**: `success`, `no_results`, `error`, `no_api_key`
- **Tracked searches**: Wikipedia, Google Fact Check, Web Search
- **Visibility**:
  - API response includes `search_status` field in `FinalAssessment`
  - Helps distinguish between "no evidence found" vs "search failed"

This transparency helps students understand when API keys are missing or searches encounter errors, improving educational value.

## Quickstart

### 1. Backend
```bash
cd fullstack-app/backend
# Create .env (see backend/.env.example)
# Required: OPENAI_API_KEY
# Optional: GOOGLE_FACT_CHECK_API_KEY, WIKIPEDIA_ACCESS_TOKEN

python -m venv .venv && .\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Health check: `http://localhost:8000/api/health`

### 2. Frontend
```bash
cd fullstack-app/frontend
# Create .env with VITE_API_URL=http://localhost:8000

npm install
npm run dev  # default: http://localhost:5173
```

## Key Endpoints (Backend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Readiness check |
| `/api/config/domain-categories` | GET | Domain taxonomy for UI docs |
| `/api/extract` | POST | Extract claims from text (no verification), returns claims with worthiness scores |
| `/api/verify` | POST | Fact-check text or selected claims, returns `FinalAssessment` |
| `/api/compare` | POST | Compare student claims with AI results, returns educational feedback |

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

## Usage Examples

### Python (Direct Import)
```python
# New minimal API
from app.core import verify_claims, FinalAssessment

# Backward compatible import
from app.core.MetaCheck import verify_claims, FinalAssessment

# Run verification
result = await verify_claims("Some text with claims", mode="basic")
print(result.claim_results)
```

### HTTP API
```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "The Earth is round.", "mode": "basic"}'
```

## Frontend Highlights

- **Your Assessment**: Students create multiple claims with verdicts, confidence, reasoning, and sources
- **AI Analysis**: Two-step workflow with claim preview and selection:
  - Step 1: Extract claims from text (max 2,000 characters)
  - Step 2: Preview extracted claims with worthiness scores (5 per page, paginated navigation)
  - Step 3: Select which claims to verify (checkbox UI)
  - Step 4: View verification results with detailed evidence and metacognition
- **Compare**: Side-by-side student vs AI verdicts/confidence/sources with AI-powered analysis
- **Documentation**: In-app user guide (workflow, modes, verdicts, weighting, limits) plus domain taxonomy reference

## Notes

- Domain config path is driven by `METACHECK_CONFIG_PATH` env var; defaults to `backend/app/config/config.json`
- Long-running verification can exceed 45s; frontend timeout is 120s
- Basic mode returns concise output; comprehensive mode includes full metacognitive detail
