# MetaCheck Frontend (React + Vite)

UI for student assessments, AI analysis, comparison, and documentation (domain taxonomy). Built with Vite, React 19, Tailwind, shadcn-style components, framer-motion.
Verdicts displayed: `SUPPORTED`, `REFUTED`, `INSUFFICIENT_INFORMATION`, `CONFLICTING_EVIDENCE`.

## Setup
1. `cd fullstack-app/frontend`
2. Create `.env` with `VITE_API_URL=http://localhost:8000` (or your backend URL)
3. Install deps: `npm install`
4. Run dev server: `npm run dev` (defaults to `http://localhost:5173`)

## Views (tabs)
- **Your Assessment**: optional student verdict/confidence/reasoning capture.
- **AI Analysis**: run `/api/verify`, see summaries and per-claim detail.
- **Compare**: side-by-side student vs AI verdicts/confidence/sources.
- **Documentation**: domain credibility categories from backend config.

## Notes
- Expects backend configured with `OPENAI_API_KEY` (standard OpenAI only).
- API timeout raised to 120s to accommodate longer MetaCheck runs.
- Key components: `ClaimCard`, `ClaimDetail`, `StudentAssessmentForm`, `ComparePanel`, `DomainLegend`.
