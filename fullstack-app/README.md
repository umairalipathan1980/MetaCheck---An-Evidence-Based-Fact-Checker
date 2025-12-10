# MetaCheck 

MetaCheck is an educational fact-checking tool that makes AI reasoning transparent. It:
- Extracts verifiable claims from text
- Searches web, Wikipedia, and fact-check APIs for evidence
- Classifies domain credibility via a configurable taxonomy
- Weighs evidence and issues structured verdicts with confidence
- Surfaces full metacognitive detail for students (search strategy, stance, uncertainties, assumptions, verdict reasoning)

Stack: FastAPI backend + React/Vite frontend (Tailwind + shadcn-style components) powered by the core `MetaCheck.py` orchestrator. Uses standard OpenAI (`OPENAI_API_KEY`) plus optional Google Fact Check and Wikipedia keys.
Verdicts: `SUPPORTED`, `REFUTED`, `INSUFFICIENT_INFORMATION`, `CONFLICTING_EVIDENCE`.

## Main components
- **MetaCheck core (`backend/app/core/MetaCheck.py`)**: Multi-agent orchestration, models for claims/evidence/metacognitive detail, domain classification helpers.
- **Domain taxonomy (`backend/app/config/config.json`)**: Credibility scores and categories used for domain credibility.
- **Backend (`fullstack-app/backend`)**: FastAPI service exposing health, domain-config, and verification APIs.
- **Frontend (`fullstack-app/frontend`)**: Student-facing UI for optional self-assessment, AI analysis, comparison, and documentation.

## Quickstart
1) Backend
   - `cd fullstack-app/backend`
   - Create `.env` (see backend/.env.example) with `OPENAI_API_KEY` and optional `GOOGLE_FACT_CHECK_API_KEY`, `WIKIPEDIA_ACCESS_TOKEN`
   - `python -m venv .venv && .\.venv\Scripts\activate`
   - `pip install -r requirements.txt`
   - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
   - Health: `http://localhost:8000/api/health`

2) Frontend
   - `cd fullstack-app/frontend`
   - Create `.env` with `VITE_API_URL=http://localhost:8000`
   - `npm install`
   - `npm run dev` (default `http://localhost:5173`)

## Key endpoints (backend)
- `GET /api/health` – readiness check
- `GET /api/config/domain-categories` – domain taxonomy for UI docs
- `POST /api/verify` – body: `{ text: string, verbose?: boolean }`; returns `FinalAssessment` with claims, evidence, and metacognitive details

## Frontend highlights
- Student assessment capture (optional) and summary
- AI analysis input + results (claims overview + detailed evidence/metacognition)
- Comparison panel (student vs AI verdict/confidence/sources)
- Documentation tab with domain taxonomy

## Notes
- Domain config path is driven by `METACHECK_CONFIG_PATH` (set in backend service wrapper); defaults to backend/app/config/config.json.
- Long-running verification can exceed 45s; frontend timeout is increased to 120s.
