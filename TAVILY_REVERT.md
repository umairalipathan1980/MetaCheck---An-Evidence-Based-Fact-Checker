# Revert to WebSearchTool + wiki_fact_evidence_tool

## What Changed

Replaced WebSearchTool + wiki_fact_evidence_tool with comprehensive_evidence_tool:
- **Before**: WebSearchTool (agent-driven) + wiki_fact_evidence_tool (parallel Wiki+Fact) = 2 turns
- **After**: comprehensive_evidence_tool (parallel Tavily+Wiki+Fact) = 1 turn

## Expected Benefits of Current Implementation

- **40% fewer turns** (3 turns instead of 5 per claim)
- **50% faster evidence gathering** (1 turn instead of 2)
- **~$0.08-0.14 savings per 5-claim workflow**
- **Total ~89% cost reduction** from $2.76 to ~$0.30

## How to Revert

If the Tavily integration causes issues, follow these steps to revert to WebSearchTool:

---

### Step 1: Revert `backend/app/core/agents.py`

#### Line 7: Restore WebSearchTool import

**Current:**
```python
from agents import Agent, ModelSettings
```

**Revert to:**
```python
from agents import Agent, WebSearchTool, ModelSettings
```

#### Line 16: Change tool import

**Current:**
```python
from app.core.tools import comprehensive_evidence_tool  # Parallel Tavily + Wikipedia + Fact Check
# REVERT TO PARALLEL: Uncomment line below to use wiki_fact_evidence_tool (without Tavily)
# from app.core.tools import wiki_fact_evidence_tool
```

**Revert to:**
```python
from app.core.tools import wiki_fact_evidence_tool  # Parallel Wikipedia + Fact Check
```

#### Lines 64-76: Revert orchestrator instructions

**Current:**
```python
    instructions=f"""Fact-check orchestrator. For each claim:
1. Use comprehensive_evidence_tool to gather ALL evidence (Tavily web search + Wikipedia + Google Fact Check) in parallel
2. comprehensive_evidence_tool returns EvidenceBundle with structured Evidence objects from all three sources
3. Extract Evidence objects from EvidenceBundle and use them for verdict determination
4. Apply verdict criteria:
   - SUPPORTED: Multiple credible sources (≥0.7) confirm, no contradictions
   - REFUTED: Credible sources (≥0.7) explicitly contradict
   - INSUFFICIENT_INFORMATION: <2 sources OR all <0.7 credibility
   - CONFLICTING_EVIDENCE: Credible sources disagree
5. Return VerificationResult with claim, verdict, confidence (0-1), justification (1-2 sentences), key_sources (format: "Name [url]"), evidence_list

CRITICAL: Include actual URLs in key_sources. Evidence is already limited by mode (basic=3+2+2, comprehensive=5+3+3).
"""
```

**Revert to:**
```python
    instructions=f"""Fact-check orchestrator. For each claim:
1. Use WebSearchTool for web evidence, wiki_fact_evidence_tool for Wikipedia + fact-check evidence (runs in parallel)
2. wiki_fact_evidence_tool returns EvidenceBundle with structured Evidence objects already populated
3. Create Evidence objects from WebSearchTool results with: source_name, source_type ("web_search"), url, snippet, relevance_score, credibility_score (0.5-0.85), stance
4. Apply verdict criteria:
   - SUPPORTED: Multiple credible sources (≥0.7) confirm, no contradictions
   - REFUTED: Credible sources (≥0.7) explicitly contradict
   - INSUFFICIENT_INFORMATION: <2 sources OR all <0.7 credibility
   - CONFLICTING_EVIDENCE: Credible sources disagree
5. Return VerificationResult with claim, verdict, confidence (0-1), justification (1-2 sentences), key_sources (format: "Name [url]"), evidence_list

CRITICAL: Include actual URLs in key_sources. Process top 3-5 web results only for efficiency.
"""
```

#### Lines 77-88: Revert tools list

**Current:**
```python
    tools=[
        claim_extractor.as_tool(
            tool_name="claim_extractor",
            tool_description="Extract verifiable claims from text. Returns a list of claims."
        ),
        comprehensive_evidence_tool,  # Parallel Tavily + Wikipedia + Fact Check (all-in-one)
        # REVERT TO PARALLEL: Replace line above with these to use wiki_fact_evidence_tool (no Tavily):
        # wiki_fact_evidence_tool,
        # REVERT TO WEBSEARCH: Replace line above with these to use WebSearchTool:
        # WebSearchTool(),
        # wiki_fact_evidence_tool,
    ],
```

**Revert to:**
```python
    tools=[
        claim_extractor.as_tool(
            tool_name="claim_extractor",
            tool_description="Extract verifiable claims from text. Returns a list of claims."
        ),
        WebSearchTool(),
        wiki_fact_evidence_tool,  # Parallel Wikipedia + Fact Check (faster than sequential)
    ],
```

---

### Step 2: Revert `backend/app/core/workflow.py`

#### Lines 27-32: Remove tavily status import

**Current:**
```python
from app.core.tools import (
    get_last_wikipedia_status,
    get_last_google_fact_check_status,
    get_last_tavily_status,
    reset_search_statuses,
)
```

**Revert to:**
```python
from app.core.tools import (
    get_last_wikipedia_status,
    get_last_google_fact_check_status,
    reset_search_statuses,
)
```

#### Lines 203-210: Revert tools comment

**Current:**
```python
    # ----------------------------------------------------------------------
    # Step 2: Analyze each claim in parallel via orchestrator agents
    # Each claim gets its own orchestrator agent with:
    # - comprehensive_evidence_tool (Tavily + Wikipedia + Fact Check all in parallel)
    # Domain credibility scoring is handled via direct config lookup after evidence gathering.
    # The orchestrator sees ALL evidence before making a verdict decision.
    # All claims run in parallel (bounded by semaphore)
    # ----------------------------------------------------------------------
```

**Revert to:**
```python
    # ----------------------------------------------------------------------
    # Step 2: Analyze each claim in parallel via orchestrator agents
    # Each claim gets its own orchestrator agent with all tools:
    # - WebSearchTool (web search)
    # - wiki_fact_evidence_tool (Wikipedia + Fact Check in parallel)
    # Domain credibility scoring is handled via direct config lookup after evidence gathering.
    # The orchestrator sees ALL evidence before making a verdict decision.
    # All claims run in parallel (bounded by semaphore)
    # ----------------------------------------------------------------------
```

#### Lines 214-222: Revert docstring

**Current:**
```python
    async def analyze_claim(claim_text: str):
        """
        Analyze a single claim using the orchestrator agent.

        The orchestrator has access to:
        - comprehensive_evidence_tool (Tavily + Wikipedia + Fact Check in parallel - returns structured EvidenceBundle)

        Domain credibility classification is applied via direct config lookup after evidence gathering.
        This ensures the agent sees ALL evidence before making a verdict decision.
        """
```

**Revert to:**
```python
    async def analyze_claim(claim_text: str):
        """
        Analyze a single claim using the orchestrator agent.

        The orchestrator has access to ALL tools:
        - WebSearchTool (web search)
        - wiki_fact_evidence_tool (Wikipedia + Fact Check in parallel - returns structured EvidenceBundle)

        Domain credibility classification is applied via direct config lookup after evidence gathering.
        This ensures the agent sees ALL evidence before making a verdict decision.
        """
```

#### Lines 250-253: Revert runtime prompt

**Current:**
```python
                    "Use comprehensive_evidence_tool to gather ALL evidence in one parallel call.\n"
                    "It runs Tavily web search + Wikipedia + Google Fact Check simultaneously.\n"
                    "Extract Evidence objects from the returned EvidenceBundle.\n"
                    "Synthesize ALL evidence from all sources before determining your verdict.\n\n"
```

**Revert to:**
```python
                    "Use WebSearchTool for web evidence and wiki_fact_evidence_tool for Wikipedia + fact-check evidence (parallel).\n"
                    "wiki_fact_evidence_tool returns structured EvidenceBundle - extract Evidence objects from it.\n"
                    "Synthesize ALL evidence from all sources before determining your verdict.\n\n"
```

#### Lines 263-273: Remove tavily status tracking

**Current:**
```python
            # Get search statuses from tools (updated by orchestrator's tool calls)
            web_status = get_last_tavily_status()
            wiki_status = get_last_wikipedia_status()
            fact_status = get_last_google_fact_check_status()

            # Default statuses if tools weren't called
            if web_status is None:
                web_status = SearchStatus(tool="web_search", status="no_results", results_count=0)
            if wiki_status is None:
                wiki_status = SearchStatus(tool="wikipedia", status="no_results", results_count=0)
            if fact_status is None:
```

**Revert to:**
```python
            # Get search statuses from tools (updated by orchestrator's tool calls)
            wiki_status = get_last_wikipedia_status()
            fact_status = get_last_google_fact_check_status()

            # Default statuses if tools weren't called
            if wiki_status is None:
                wiki_status = SearchStatus(tool="wikipedia", status="no_results", results_count=0)
            if fact_status is None:
```

#### Lines 308-309: Add back web status inference

**Current:**
```python
            normalize_key_sources(claim_result)

            # web_status is now tracked directly by comprehensive_evidence_tool
            # No need to infer from evidence list

            # Create per-claim search status summary
```

**Revert to:**
```python
            normalize_key_sources(claim_result)

            # Infer web search status from agent's evidence
            web_evidence = [e for e in claim_result.evidence_list if e.source_type == "web_search"]
            if web_evidence:
                web_status = SearchStatus(
                    tool="web_search",
                    status="success",
                    results_count=len(web_evidence)
                )
            else:
                web_status = SearchStatus(
                    tool="web_search",
                    status="no_results",
                    results_count=0
                )

            # Create per-claim search status summary
```

---

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C in terminal)
# Restart backend
cd fullstack-app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Testing After Revert

1. Run a simple verification with 2-3 claims
2. Check that evidence appears from WebSearchTool, Wikipedia, and Google Fact Check
3. Verify search status tracking still works (search_status in API response)
4. Confirm turns per claim increased from 3 to 5 (expected behavior)

---

## Notes

- The TavilyClient and comprehensive_evidence_tool remain in `clients.py` and `tools.py` but are unused after revert
- No need to remove them - they don't impact performance when not called
- Both approaches use the same underlying clients (WikipediaClient, GoogleFactCheckClient)
- Status tracking for Wikipedia and Fact Check works identically in both versions
- WebSearchTool provides agent-driven iterative search refinement that Tavily does not
- If reverting, you'll regain search flexibility but lose speed and cost benefits

---

## Alternative: Revert to Parallel Wiki+Fact Only (Keep Tavily Out)

If you want to keep using parallel wiki+fact but remove only Tavily (without going back to WebSearchTool), follow the revert instructions above but keep comprehensive_evidence_tool out. Use this in agents.py:

```python
from agents import Agent, WebSearchTool, ModelSettings
from app.core.tools import wiki_fact_evidence_tool
```

And in the tools list:
```python
tools=[
    claim_extractor.as_tool(...),
    WebSearchTool(),
    wiki_fact_evidence_tool,
]
```

This gives you the parallel wiki+fact benefit without Tavily's single-query limitation.
