# Parallel Evidence Tool - Revert Instructions

## What Changed

Replaced two sequential tools with one parallel tool:
- **Before**: `wikipedia_search_tool` → `google_fact_check_tool` (2 turns, sequential)
- **After**: `wiki_fact_evidence_tool` (1 turn, parallel execution)

## Expected Benefits

- **20% fewer API calls** (4 turns instead of 5 per claim)
- **40-50% faster evidence gathering** (parallel vs sequential)
- **Structured output** (EvidenceBundle with Evidence objects instead of text parsing)
- **~15,000 tokens saved per 5-claim workflow** (~$0.03-0.12 cost savings)

## How to Revert

If the parallel tool causes issues, revert by following these steps:

### 1. Edit `backend/app/core/agents.py` (Line 16-18)

**Current (Parallel):**
```python
from app.core.tools import wiki_fact_evidence_tool  # Parallel tool (Wikipedia + Fact Check)
# REVERT: Uncomment line below and remove line above to use sequential tools
# from app.core.tools import wikipedia_search_tool, google_fact_check_tool
```

**Revert to (Sequential):**
```python
from app.core.tools import wikipedia_search_tool, google_fact_check_tool
```

### 2. Edit `backend/app/core/agents.py` (Line 80-84)

**Current (Parallel):**
```python
    tools=[
        claim_extractor.as_tool(...),
        WebSearchTool(),
        wiki_fact_evidence_tool,  # Parallel Wikipedia + Fact Check (faster than sequential)
        # REVERT: Replace line above with these two lines to use sequential tools:
        # wikipedia_search_tool,
        # google_fact_check_tool,
    ],
```

**Revert to (Sequential):**
```python
    tools=[
        claim_extractor.as_tool(...),
        WebSearchTool(),
        wikipedia_search_tool,
        google_fact_check_tool,
    ],
```

### 3. Edit `backend/app/core/agents.py` (Line 61-63)

**Current (Parallel):**
```python
1. Use WebSearchTool for web evidence, wiki_fact_evidence_tool for Wikipedia + fact-check evidence (runs in parallel)
2. wiki_fact_evidence_tool returns EvidenceBundle with structured Evidence objects already populated
3. Create Evidence objects from WebSearchTool results with: source_name, source_type ("web_search"), url, snippet, relevance_score, credibility_score (0.5-0.85), stance
```

**Revert to (Sequential):**
```python
1. Use WebSearchTool, wikipedia_search_tool, google_fact_check_tool to gather evidence
2. Create Evidence objects with: source_name, source_type ("web_search"/"wikipedia"/"fact_check"), url, snippet, relevance_score, credibility_score (fact_check=0.95, wikipedia=0.8, web=0.5-0.85), stance ("supports"/"refutes"/"neutral"/"unclear")
```

### 4. Edit `backend/app/core/workflow.py` (Line 251-252)

**Current (Parallel):**
```python
"Use WebSearchTool for web evidence and wiki_fact_evidence_tool for Wikipedia + fact-check evidence (parallel).\n"
"wiki_fact_evidence_tool returns structured EvidenceBundle - extract Evidence objects from it.\n"
```

**Revert to (Sequential):**
```python
"Use WebSearchTool, wikipedia_search_tool, and google_fact_check_tool to gather evidence.\n"
```

### 5. Restart Backend

```bash
# Stop backend (Ctrl+C)
# Restart backend
cd fullstack-app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing After Revert

1. Run a simple verification with 2-3 claims
2. Check that Wikipedia and Google Fact Check results appear in evidence
3. Verify search status tracking still works (search_status in API response)

## Notes

- The parallel tool (`wiki_fact_evidence_tool`) is already implemented and tested in `tools.py`
- Both approaches use the same underlying clients (WikipediaClient, GoogleFactCheckClient)
- Status tracking works identically in both versions (global status variables)
- If reverting, you'll lose the parallelization benefit but functionality remains identical
