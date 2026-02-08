"""
MetaCheck Function Tools

Function tools for agent use (Wikipedia search, Google Fact Check).
Includes status tracking for search success/failure visibility.
"""

import asyncio
from agents import function_tool

from app.core.clients import google_fact_check_client, wikipedia_client, tavily_client
from app.core.models import SearchStatus, EvidenceBundle, SearchStatusSummary


# Global status tracking (updated by tools, read by workflow)
_last_wikipedia_status: SearchStatus = None
_last_google_fact_check_status: SearchStatus = None
_last_tavily_status: SearchStatus = None


def get_last_wikipedia_status() -> SearchStatus:
    """Get the status of the last Wikipedia search"""
    return _last_wikipedia_status


def get_last_google_fact_check_status() -> SearchStatus:
    """Get the status of the last Google Fact Check search"""
    return _last_google_fact_check_status


def get_last_tavily_status() -> SearchStatus:
    """Get the status of the last Tavily search"""
    return _last_tavily_status


def reset_search_statuses():
    """Reset search statuses for a new verification run"""
    global _last_wikipedia_status, _last_google_fact_check_status, _last_tavily_status
    _last_wikipedia_status = None
    _last_google_fact_check_status = None
    _last_tavily_status = None


# ============================================================================
# WIKIPEDIA SEARCH TOOL
# ============================================================================

@function_tool
async def wikipedia_search_tool(claim: str) -> str:
    """
    Retrieve evidence from Wikipedia.

    Args:
        claim: The factual claim to search for

    Returns:
        Formatted string with Wikipedia evidence and status
    """
    global _last_wikipedia_status

    evidence, status = await wikipedia_client.search_for_claim_async(claim, max_results=2)
    _last_wikipedia_status = status

    # Include status in response so it's visible
    status_prefix = ""
    if status.status == "error":
        status_prefix = f"[SEARCH ERROR: {status.error_message}] "
    elif status.status == "no_results":
        status_prefix = "[SEARCH OK - NO RESULTS] "

    if not evidence:
        if status.status == "error":
            return f"{status_prefix}Wikipedia search failed: {status.error_message}"
        return f"{status_prefix}No Wikipedia evidence found."

    result = f"[SEARCH OK] Retrieved {len(evidence)} pieces of Wikipedia evidence:\n\n"
    for i, ev in enumerate(evidence, 1):
        result += f"{i}. {ev.source_name}\n"
        result += f"   URL: {ev.url}\n"
        result += f"   Snippet: {ev.snippet}\n"
        result += f"   Credibility: {ev.credibility_score}\n\n"

    return result


# ============================================================================
# GOOGLE FACT CHECK TOOL
# ============================================================================

@function_tool
async def google_fact_check_tool(claim: str) -> str:
    """
    Query Google Fact Check API for professional fact-checks.

    Args:
        claim: The factual claim to fact-check

    Returns:
        Formatted string with fact-check results and status
    """
    global _last_google_fact_check_status

    evidence, status = await google_fact_check_client.search_fact_checks_async(claim, max_results=5)
    _last_google_fact_check_status = status

    # Include status in response so it's visible
    if status.status == "no_api_key":
        return "[NO API KEY] Google Fact Check API key not configured. Fact-check database queries are disabled."
    elif status.status == "error":
        return f"[SEARCH ERROR] Google Fact Check API failed: {status.error_message}"

    if not evidence:
        return "[SEARCH OK - NO RESULTS] No professional fact-checks found for this claim."

    result = f"[SEARCH OK] Found {len(evidence)} professional fact-checks:\n\n"
    for i, ev in enumerate(evidence, 1):
        result += f"{i}. {ev.source_name}\n"
        result += f"   URL: {ev.url}\n"
        result += f"   Assessment: {ev.snippet}\n"
        result += f"   Stance: {ev.stance}\n\n"

    return result


# ============================================================================
# PARALLEL EVIDENCE TOOL (Wikipedia + Fact Check)
# ============================================================================

@function_tool
async def wiki_fact_evidence_tool(claim: str) -> EvidenceBundle:
    """
    Run Wikipedia and Google Fact Check in parallel for a claim and return structured evidence.
    """
    reset_search_statuses()

    wiki_task = wikipedia_client.search_for_claim_async(claim, max_results=2)
    fact_task = google_fact_check_client.search_fact_checks_async(claim, max_results=5)

    (wiki_evidence, wiki_status), (fact_evidence, fact_status) = await asyncio.gather(
        wiki_task, fact_task
    )

    global _last_wikipedia_status, _last_google_fact_check_status
    _last_wikipedia_status = wiki_status
    _last_google_fact_check_status = fact_status

    status_summary = SearchStatusSummary(
        wikipedia=wiki_status,
        google_fact_check=fact_status,
    )

    # Combine evidence from both sources
    combined = []
    combined.extend(wiki_evidence or [])
    combined.extend(fact_evidence or [])

    return EvidenceBundle(evidence=combined, search_status=status_summary)


# ============================================================================
# COMPREHENSIVE EVIDENCE TOOL (Tavily + Wikipedia + Fact Check)
# ============================================================================

@function_tool
async def comprehensive_evidence_tool(claim: str, mode: str = "basic") -> EvidenceBundle:
    """
    Run Tavily, Wikipedia, and Google Fact Check in parallel for comprehensive evidence gathering.

    Args:
        claim: The factual claim to verify
        mode: "basic" or "comprehensive" - affects result limits

    Returns:
        EvidenceBundle with all evidence and search status summary
    """
    reset_search_statuses()

    # Load source limits from settings
    from app.core.tool_settings import load_tool_settings
    tool_settings = load_tool_settings()
    mode_settings = tool_settings["verification_scope"][mode]

    max_web = int(mode_settings.get("max_web_sources", 3 if mode == "basic" else 5))
    max_wiki = int(mode_settings.get("max_wikipedia_sources", 2 if mode == "basic" else 3))
    max_fact = int(mode_settings.get("max_fact_check_sources", 2 if mode == "basic" else 3))

    # Create parallel tasks
    tavily_task = tavily_client.search_async(claim, max_results=max_web, search_depth="basic")
    wiki_task = wikipedia_client.search_for_claim_async(claim, max_results=max_wiki)
    fact_task = google_fact_check_client.search_fact_checks_async(claim, max_results=max_fact)

    # Execute in parallel
    (web_evidence, web_status), (wiki_evidence, wiki_status), (fact_evidence, fact_status) = await asyncio.gather(
        tavily_task, wiki_task, fact_task
    )

    # Update global status tracking
    global _last_tavily_status, _last_wikipedia_status, _last_google_fact_check_status
    _last_tavily_status = web_status
    _last_wikipedia_status = wiki_status
    _last_google_fact_check_status = fact_status

    # Create status summary
    status_summary = SearchStatusSummary(
        web_search=web_status,
        wikipedia=wiki_status,
        google_fact_check=fact_status,
    )

    # Combine evidence from all sources
    combined = []
    combined.extend(web_evidence or [])
    combined.extend(wiki_evidence or [])
    combined.extend(fact_evidence or [])

    return EvidenceBundle(evidence=combined, search_status=status_summary)
