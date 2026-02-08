# MetaCheck Frontend (React + Vite)

UI for student assessments, AI analysis, comparison, and documentation (full user guide + domain taxonomy). Built with Vite, React 19, Tailwind, shadcn-style components, framer-motion.

Verdicts displayed: `SUPPORTED`, `REFUTED`, `INSUFFICIENT_INFORMATION`, `CONFLICTING_EVIDENCE`.

## Setup

1. `cd fullstack-app/frontend`
2. Create `.env` with `VITE_API_URL=http://localhost:8000` (or your backend URL)
3. Install deps: `npm install`
4. Run dev server: `npm run dev` (defaults to `http://localhost:5173`)

## Frontend-Backend Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Your Assessment  │  │  AI Analysis     │  │  Documentation   │
│  (Optional)      │  │                  │  │                  │
│                  │  │ Step 1: Extract  │  │  Domain          │
│ • Create claims  │  │ POST /api/extract│  │  Categories      │
│ • Verdict        │  │        │         │  │                  │
│ • Confidence     │  │        ▼         │  │  GET /api/config │
│ • Reasoning      │  │ Step 2: Preview  │  │  /domain-        │
│ • Sources        │  │ • Select claims  │  │  categories      │
└──────────────────┘  │ • Worthiness     │  └──────────────────┘
         │             │        │         │
         │             │        ▼         │
         │             │ Step 3: Verify  │
         │             │ POST /api/verify│
         │             │ (selected only) │
         │             └────────┼─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │   Compare View       │
         │   Student vs AI      │
         │   • Verdicts         │
         │   • Confidence       │
         │   • Sources          │
         │   • AI Analysis      │
         │   POST /api/compare  │
         └──────────────────────┘

Backend Processing (two-step workflow):
────────────────────────────────────────
Step 1: POST /api/extract { text, mode }
  │
  └─> claim_extractor agent → Returns claims with worthiness scores

Step 2: POST /api/verify { text, mode, selected_claim_indices }
  │
  ├─> Filter to selected claims only
  │
  ├─> For each selected claim in parallel (max 5 basic / 5 comprehensive):
  │     orchestrator agent
  │       ├─> WebSearchTool
  │       ├─> wikipedia_search_tool
  │       ├─> google_fact_check_tool
  │       └─> domain_classification_tool
  │
  └─> Returns FinalAssessment {
        claim_results,
        search_status,
        overall_credibility
      }
```

## Views (Tabs)

| Tab | Description |
|-----|-------------|
| **Your Assessment** | Students create multiple claims with verdicts, confidence, reasoning, sources (CRUD interface) |
| **AI Analysis** | Three-step workflow: Extract claims → Preview & select → Verify selected claims |
| **Compare** | Side-by-side student vs AI comparison with AI-powered feedback analysis |
| **Documentation** | Full in-app user documentation plus domain credibility categories from backend config |

## Key Components

```
src/components/
├── analysis/
│   ├── ClaimCard.jsx         # Compact claim display with verdict badge
│   ├── ClaimDetail.jsx       # Full claim analysis with evidence breakdown
│   ├── ClaimPreview.jsx      # NEW: Claim selection UI with worthiness scores
│   ├── StudentAssessment.jsx # Multi-claim CRUD interface with verdict/confidence/reasoning
│   ├── ComparePanel.jsx      # Student vs AI comparison with AI analysis
│   └── DomainLegend.jsx      # Domain category documentation
└── ui/
    ├── badge.jsx             # Status/verdict badges
    ├── button.jsx            # Reusable button
    ├── card.jsx              # Container card
    ├── input.jsx             # Text input
    └── textarea.jsx          # Multi-line input
```

## Features

- **Text Length Limit**: 2,000 character maximum with real-time character counter
- **Claim Preview & Selection**: View extracted claims with worthiness scores, select which to verify
- **Paginated View**: 5 claims displayed per page with Previous/Next navigation buttons
- **Smart Claim Limits**: Configurable via Settings (default: 5 basic, 3 comprehensive)
- **Multi-Claim Student Assessment**: Create multiple claims with full CRUD operations (add, edit, delete)
- **Mode Selection**: Choose between `basic` (concise) or `comprehensive` (full metacognitive detail)
- **Real-time Elapsed Time**: Track verification duration
- **Evidence Breakdown**: View sources by type (web, Wikipedia, fact-check)
- **Stance Analysis**: See supporting, refuting, neutral, unclear evidence counts
- **Concise Comparison Feedback**: Get brief summary + areas for improvement (not verbose)
- **Configurable Settings**: Adjust verification scope, model choice, timeouts, source limits, Tavily search depth
- **Automatic Backend Reload**: Settings changes apply immediately without server restart
- **Clickable Sources**: All sources are clickable links to original web pages

## Notes

- Expects backend running with `OPENAI_API_KEY` configured
- API timeout is 120s to accommodate longer MetaCheck runs (typical: 30-90s)
- Backend modular architecture: see `backend/README.md` for details
