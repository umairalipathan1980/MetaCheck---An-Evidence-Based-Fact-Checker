"""
MetaCheck Workflow

Main verification workflow function.
"""

import asyncio
import os
from typing import Literal

from agents import Runner

import re
from typing import List, Optional

from app.core.models import (
    FinalAssessment,
    OrchestratorOutput,
    SearchStatus,
    SearchStatusSummary,
    Evidence,
    VerificationResult,
)
from app.core.analysis import MetacognitiveTracker
from app.core.agents import claim_extractor, orchestrator
from app.core.domain import classify_web_source
from app.core.tool_settings import load_tool_settings
from app.core.tools import (
    get_last_wikipedia_status,
    get_last_google_fact_check_status,
    get_last_tavily_status,
    reset_search_statuses,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def merge_evidence(
    result: VerificationResult,
    wiki_evidence: List[Evidence],
    fact_evidence: List[Evidence]
) -> None:
    """Merge Wikipedia and Fact Check evidence into result, avoiding duplicates."""
    existing_urls = {e.url for e in result.evidence_list if e.url}

    for evidence in (wiki_evidence or []) + (fact_evidence or []):
        if evidence.url and evidence.url not in existing_urls:
            result.evidence_list.append(evidence)
            existing_urls.add(evidence.url)


def normalize_key_sources(result: VerificationResult) -> None:
    """Normalize key_sources to 'Label [url]' format and include all evidence URLs."""
    url_pattern = re.compile(r"(https?://[^\s\]]+)")

    def normalize_entry(entry: str) -> str:
        match = url_pattern.search(entry)
        if not match:
            return entry.strip()
        url = match.group(1)
        label = entry.replace(url, "").replace("[]", "").strip(" :|-")
        if not label:
            label = url
        return f"{label} [{url}]"

    existing_urls = set()
    normalized_sources = []

    # Start with existing key_sources
    for src in result.key_sources:
        norm = normalize_entry(src)
        match = url_pattern.search(norm)
        if match:
            url = match.group(1)
            if url in existing_urls:
                continue
            existing_urls.add(url)
        normalized_sources.append(norm)

    # Add any missing evidence URLs
    for ev in result.evidence_list:
        if ev.url and ev.url not in existing_urls:
            label = ev.source_name or ev.url
            normalized_sources.append(f"{label} [{ev.url}]")
            existing_urls.add(ev.url)

    result.key_sources = normalized_sources


def synthesize_verdict(
    claim_text: str,
    agent_output: Optional[OrchestratorOutput],
    wiki_evidence: List[Evidence],
    fact_evidence: List[Evidence],
    mode: str
) -> VerificationResult:
    """
    Synthesize verdict from all evidence sources.

    Priority:
    1. If agent produced valid output, use it and merge wiki/fact evidence
    2. If agent failed but we have wiki/fact evidence, create INSUFFICIENT_INFORMATION verdict
    3. If all sources failed, return error result
    """
    # Case 1: Agent produced valid output - use it as base
    if agent_output and agent_output.claim_results:
        result = agent_output.claim_results[0]
        merge_evidence(result, wiki_evidence, fact_evidence)
        normalize_key_sources(result)
        return result

    # Case 2: Agent failed, but we have wiki/fact evidence
    all_evidence = (wiki_evidence or []) + (fact_evidence or [])
    if all_evidence:
        return VerificationResult(
            claim=claim_text,
            verdict="INSUFFICIENT_INFORMATION",
            confidence=0.3,
            justification="Web search agent failed. Evidence from Wikipedia and fact-check databases is shown below, but automated verdict synthesis was not possible.",
            key_sources=[f"{e.source_name} [{e.url}]" for e in all_evidence[:5] if e.url],
            evidence_list=all_evidence,
            metacognitive_steps=[],
            metacognitive_detail=None
        )

    # Case 3: All sources failed
    return VerificationResult(
        claim=claim_text,
        verdict="INSUFFICIENT_INFORMATION",
        confidence=0.0,
        justification="All evidence sources failed. Unable to verify this claim.",
        key_sources=[],
        evidence_list=[],
        metacognitive_steps=[],
        metacognitive_detail=None
    )


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

async def verify_claims(
    text: str,
    mode: Literal["basic", "comprehensive"] = "basic",
    selected_claim_indices: Optional[List[int]] = None,
    selected_claim_texts: Optional[List[str]] = None,
) -> FinalAssessment:
    """
    Main MetaCheck workflow with Phase 2 metacognitive layer.

    Args:
        text: Input text containing one or more claims.
        mode: "basic" for concise output or "comprehensive" for full detail.
        selected_claim_indices: Optional list of 0-indexed claim indices to verify.
                                Used only when selected_claim_texts is not provided.
        selected_claim_texts: Optional pre-extracted claim texts selected by the user.
                              If provided, verification skips extraction and uses these claims directly.

    Returns:
        FinalAssessment with all results and metacognitive analysis
    """
    selected_mode = mode.lower()
    if selected_mode not in {"basic", "comprehensive"}:
        raise ValueError(f"Invalid mode '{mode}'. Expected 'basic' or 'comprehensive'.")

    tracker = MetacognitiveTracker()
    tool_settings = load_tool_settings()
    per_claim_timeout_seconds = float(
        tool_settings.get("performance_cost_controls", {}).get("per_claim_timeout_seconds", 90)
    )

    # ----------------------------------------------------------------------
    # Step 1: Determine claims to verify
    # ----------------------------------------------------------------------
    if selected_claim_texts:
        claim_texts = [claim_text for claim_text in selected_claim_texts if claim_text]
    else:
        extracted = await Runner.run(
            claim_extractor,
            text,
        )
        claim_list = extracted.final_output
        claims = claim_list.claims if claim_list else []
        claim_texts = [claim.text for claim in claims]

    if not claim_texts:
        assessment = FinalAssessment(
            input_text=text,
            total_claims=0,
            claim_results=[],
            overall_credibility="Average Confidence: 0.00",
            mode=selected_mode,
        )
        return assessment

    # Filter claims by selected indices if provided (only when we extracted inside verify)
    if selected_claim_indices is not None and not selected_claim_texts:
        # Validate indices
        valid_indices = [i for i in selected_claim_indices if 0 <= i < len(claim_texts)]
        if not valid_indices:
            assessment = FinalAssessment(
                input_text=text,
                total_claims=0,
                claim_results=[],
                overall_credibility="Average Confidence: 0.00",
                mode=selected_mode,
            )
            return assessment
        # Filter claims to only selected ones
        claim_texts = [claim_texts[i] for i in sorted(valid_indices)]

    # ----------------------------------------------------------------------
    # Step 2: Analyze each claim in parallel via orchestrator agents
    # Each claim gets its own orchestrator agent with:
    # - comprehensive_evidence_tool (Tavily + Wikipedia + Fact Check all in parallel)
    # Domain credibility scoring is handled via direct config lookup after evidence gathering.
    # The orchestrator sees ALL evidence before making a verdict decision.
    # All claims run in parallel (bounded by semaphore)
    # ----------------------------------------------------------------------
    semaphore = asyncio.Semaphore(int(os.getenv("METACHECK_MAX_CONCURRENCY", "5")))

    async def analyze_claim(claim_text: str):
        """
        Analyze a single claim using the orchestrator agent.

        The orchestrator has access to:
        - comprehensive_evidence_tool (Tavily + Wikipedia + Fact Check in parallel - returns structured EvidenceBundle)

        Domain credibility classification is applied via direct config lookup after evidence gathering.
        This ensures the agent sees ALL evidence before making a verdict decision.
        """
        async with semaphore:
            # Reset search statuses for this claim
            reset_search_statuses()

            # Build mode-specific instructions
            if selected_mode == "basic":
                mode_instruction = (
                    "MODE: BASIC - Concise output.\n"
                    "- justification: ONE sentence explaining verdict\n"
                    "- metacognitive_steps: []\n"
                    "- metacognitive_detail: null\n"
                    "- Process top 3 web results, 2 Wikipedia, 2 fact-check\n"
                )
            else:  # comprehensive
                mode_instruction = (
                    "MODE: COMPREHENSIVE - Full analysis.\n"
                    "- Populate metacognitive_steps with reasoning\n"
                    "- Populate metacognitive_detail with: search_queries, sources_assessed, verdict_reasoning, ai_uncertainties, assumptions_made, potential_weaknesses, metacognitive_summary\n"
                    "- Process top 5 web results, 3 Wikipedia, 3 fact-check\n"
                )

            # Run orchestrator - it has comprehensive_evidence_tool to gather all evidence
            agent_result = await Runner.run(
                orchestrator,
                (
                    f"{mode_instruction}\n"
                    "Use comprehensive_evidence_tool to gather ALL evidence in one parallel call.\n"
                    "It runs Tavily web search + Wikipedia + Google Fact Check simultaneously.\n"
                    "Extract Evidence objects from the returned EvidenceBundle.\n"
                    "Synthesize ALL evidence from all sources before determining your verdict.\n\n"
                    f"Claim to verify: {claim_text}"
                ),
                max_turns=5,  # Optimized for cost efficiency (was 15)
                # REVERT: Change tools in agents.py and update prompt above to use WebSearchTool + wiki_fact_evidence_tool
            )

            # Extract agent output (may be None if agent failed)
            agent_output: OrchestratorOutput = agent_result.final_output if agent_result else None

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
                fact_status = SearchStatus(tool="google_fact_check", status="no_results", results_count=0)

            # Synthesize verdict (uses agent output, with fallback if agent failed)
            claim_result = synthesize_verdict(
                claim_text=claim_text,
                agent_output=agent_output,
                wiki_evidence=[],  # Already included by orchestrator
                fact_evidence=[],  # Already included by orchestrator
                mode=selected_mode
            )

            # Apply domain-based credibility classification to web search evidence
            # This replaces the agent's domain_classification_tool with direct config lookup
            # Also limit web results processed (top 3 for basic, top 5 for comprehensive)
            max_web_results = 3 if selected_mode == "basic" else 5
            web_evidence_count = 0
            filtered_evidence = []

            for evidence in claim_result.evidence_list:
                # Limit web search results for efficiency
                if evidence.source_type == "web_search":
                    if web_evidence_count >= max_web_results:
                        continue  # Skip extra web results
                    web_evidence_count += 1
                    if evidence.url:
                        classification = classify_web_source(evidence.url)
                        evidence.credibility_score = classification["credibility_score"]

                filtered_evidence.append(evidence)

            claim_result.evidence_list = filtered_evidence

            normalize_key_sources(claim_result)

            # web_status is now tracked directly by comprehensive_evidence_tool
            # No need to infer from evidence list

            # Create per-claim search status summary
            claim_search_status = SearchStatusSummary(
                web_search=web_status,
                wikipedia=wiki_status,
                google_fact_check=fact_status
            )

            return claim_result, claim_search_status

    async def analyze_claim_with_timeout(claim_text: str):
        try:
            return await asyncio.wait_for(
                analyze_claim(claim_text),
                timeout=per_claim_timeout_seconds,
            )
        except asyncio.TimeoutError:
            timed_out_result = VerificationResult(
                claim=claim_text,
                verdict="INSUFFICIENT_INFORMATION",
                confidence=0.0,
                justification=(
                    f"Claim verification timed out after {per_claim_timeout_seconds:.0f} seconds."
                ),
                key_sources=[],
                evidence_list=[],
                metacognitive_steps=[],
                metacognitive_detail=None,
            )
            timed_out_status = SearchStatusSummary(
                web_search=SearchStatus(
                    tool="web_search",
                    status="error",
                    results_count=0,
                    error_message="claim timeout",
                ),
                wikipedia=SearchStatus(
                    tool="wikipedia",
                    status="error",
                    results_count=0,
                    error_message="claim timeout",
                ),
                google_fact_check=SearchStatus(
                    tool="google_fact_check",
                    status="error",
                    results_count=0,
                    error_message="claim timeout",
                ),
            )
            return timed_out_result, timed_out_status

    # Run all claim analyses in parallel (bounded by semaphore)
    claim_tasks = [analyze_claim_with_timeout(claim_text) for claim_text in claim_texts]
    claim_task_results = await asyncio.gather(*claim_tasks)

    # Extract results and statuses
    claim_results = [cr for cr, _ in claim_task_results if cr]
    claim_statuses = [status for _, status in claim_task_results if status]

    if selected_mode == "comprehensive":
        for cr in claim_results:
            if cr.metacognitive_detail:
                cr.metacognitive_detail.contradiction_detection = tracker.detect_contradictions(
                    cr.evidence_list
                )

    # Trim results for basic mode to avoid returning extra reasoning fields
    if selected_mode == "basic":
        for cr in claim_results:
            cr.metacognitive_steps = []
            cr.metacognitive_detail = None

    # Validate comprehensive mode results
    if selected_mode == "comprehensive":
        for i, cr in enumerate(claim_results):
            if cr.metacognitive_detail is None:
                print(f"WARNING: Claim {i+1} missing metacognitive_detail in comprehensive mode")
                print(f"  Claim: {cr.claim[:80]}...")
                # This indicates the agent didn't follow instructions properly

    # Aggregate search statuses from all claims
    # For each search type, aggregate results (total counts, worst status wins for errors)
    def aggregate_status(statuses: List[SearchStatus], tool: str) -> SearchStatus:
        """Aggregate statuses: sum counts, prefer errors over success."""
        if not statuses:
            return SearchStatus(tool=tool, status="no_results", results_count=0)

        total_count = sum(s.results_count for s in statuses if s)
        has_error = any(s and s.status == "error" for s in statuses)
        has_no_api_key = any(s and s.status == "no_api_key" for s in statuses)
        has_success = any(s and s.status == "success" for s in statuses)

        if has_error:
            error_msg = next((s.error_message for s in statuses if s and s.error_message), None)
            return SearchStatus(tool=tool, status="error", results_count=total_count, error_message=error_msg)
        elif has_no_api_key:
            return SearchStatus(tool=tool, status="no_api_key", results_count=0)
        elif has_success:
            return SearchStatus(tool=tool, status="success", results_count=total_count)
        else:
            return SearchStatus(tool=tool, status="no_results", results_count=0)

    web_statuses = [s.web_search for s in claim_statuses if s and s.web_search]
    wiki_statuses = [s.wikipedia for s in claim_statuses if s and s.wikipedia]
    fact_statuses = [s.google_fact_check for s in claim_statuses if s and s.google_fact_check]

    search_status_summary = SearchStatusSummary(
        web_search=aggregate_status(web_statuses, "web_search"),
        wikipedia=aggregate_status(wiki_statuses, "wikipedia"),
        google_fact_check=aggregate_status(fact_statuses, "google_fact_check"),
    )

    # Calculate overall confidence from structured results
    overall_confidence = sum(cr.confidence for cr in claim_results) / len(claim_results) if claim_results else 0.5

    # Create final assessment with structured results
    assessment = FinalAssessment(
        input_text=text,
        total_claims=len(claim_results),
        claim_results=claim_results,  # Use the structured VerificationResults
        overall_credibility=f"Average Confidence: {overall_confidence:.2f}",
        mode=selected_mode,
        search_status=search_status_summary,
    )

    return assessment
