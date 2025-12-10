# MetaCheck Backend (FastAPI)

FastAPI service exposing MetaCheck’s verification workflow for the React frontend.

## Endpoints
- `GET /api/health` – readiness check
- `GET /api/config/domain-categories` – domain credibility taxonomy (from `app/config/config.json`)
- `POST /api/verify` – body `{ text: string, verbose?: boolean }` → `FinalAssessment` (claims, evidence, metacognitive detail)

## Setup
1. `cd fullstack-app/backend`
2. Create `.env` (see `.env.example`):
   - `OPENAI_API_KEY` (required)
   - `GOOGLE_FACT_CHECK_API_KEY` (optional)
   - `WIKIPEDIA_ACCESS_TOKEN` (optional)
3. Create venv & install deps:
   - `python -m venv .venv && .\.venv\Scripts\activate`
   - `pip install -r requirements.txt`
4. Run server:
   - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Notes
- Domain config lives at `app/config/config.json`; `METACHECK_CONFIG_PATH` is set in `app/services/metacheck_service.py`.
- Frontend uses `VITE_API_URL` (defaults to `http://localhost:8000`).
- Requests can take time; frontend timeout is 120s.
