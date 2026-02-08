# Parallel Evidence Collection Plan (Orchestrator + Sub-Agents)

## Goals
- Speed up evidence gathering by running web search, Wikipedia, and Google Fact Check concurrently per claim.
- Keep the agent pattern: top-level orchestrator delegates to per-claim evidence agents; orchestrator (or a verdict agent) synthesizes into final verdicts.
- Maintain existing data models (Evidence, DomainClassification, VerificationResult) and API contract.

## Architecture
- Top-level orchestrator: extracts claims, dispatches evidence tasks, aggregates results, applies verdict criteria.
- Evidence sub-agent (per claim): encapsulates evidence gathering and returns structured evidence + metacognitive detail.
- Concurrency limits: bounded semaphore (e.g., 3–4) to avoid API overload.
- Async IO: httpx.AsyncClient for Wikipedia and Google Fact Check; async web search wrapper or existing WebSearchTool if it supports async.

## Steps
1) Prep async clients
   - Convert app/core/clients.py to async (httpx.AsyncClient with timeouts). Provide async methods: search_fact_checks_async, search_for_claim_async.
   - Keep Evidence creation the same. Handle missing API keys gracefully.

2) Async tools
   - Update app/core/tools.py to expose async function_tool versions: wikipedia_search_tool_async, google_fact_check_tool_async.
   - If WebSearchTool lacks async, wrap an async search helper (limited results) or keep sync search but run in thread executor.

3) Evidence sub-agent
   - Define a new Agent (e.g., evidence_agent) with instructions to call three tools once and return structured evidence list + domain classifications.
   - Or implement a single tool collect_evidence_async(claim) that internally gathers all three sources with asyncio.gather and returns Evidence + DomainClassification records.
   - Attach metacognitive detail (search queries, sources_assessed) in the returned payload.

4) Per-claim concurrency
   - In workflow (verify_claims), after claim extraction, dispatch evidence tasks per claim via Runner.run(evidence_agent, claim) under a semaphore.
   - Use asyncio.gather on claim tasks to parallelize claims up to the semaphore limit.

5) Verdict synthesis
   - Feed aggregated evidence per claim back to the orchestrator/verdict agent to apply VERDICT_CRITERIA and produce VerificationResult.
   - In basic mode, strip metacognitive detail as today.

6) Telemetry/limits
   - Set per-request timeouts (e.g., 8–10s) and max results (3–5) for each source.
   - Surface any tool errors/timeouts in metacognitive detail for transparency.

## Rollout notes
- Keep existing sync paths until async path is stable; feature-flag if needed.
- Update README to note parallel evidence pipeline and API timeouts.
