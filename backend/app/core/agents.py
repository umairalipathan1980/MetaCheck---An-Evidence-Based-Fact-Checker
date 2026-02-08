"""
MetaCheck Agent Definitions

Agent definitions for claim extraction and orchestration.
"""

from agents import Agent, ModelSettings

from app.core.models import ClaimList, OrchestratorOutput, ComparisonAnalysis
from app.core.constants import (
    MODEL_NAME,
    VERDICT_CRITERIA,
    METACOGNITIVE_INSTRUCTIONS,
    EXTRACTION_INSTRUCTIONS,
)
from app.core.tools import comprehensive_evidence_tool  # Parallel Tavily + Wikipedia + Fact Check
# REVERT TO PARALLEL: Uncomment line below to use wiki_fact_evidence_tool (without Tavily)
# from app.core.tools import wiki_fact_evidence_tool
# REVERT TO WEBSEARCH: Add WebSearchTool import above and use:
# from agents import Agent, WebSearchTool, ModelSettings
# from app.core.tools import wiki_fact_evidence_tool


def _model_settings(max_completion_tokens: int, temperature: float) -> ModelSettings:
    """Build model settings and omit temperature for gpt-5* models."""
    settings_kwargs = {"max_completion_tokens": max_completion_tokens}
    if not MODEL_NAME.lower().startswith("gpt-5"):
        settings_kwargs["temperature"] = temperature
    return ModelSettings(**settings_kwargs)


# ============================================================================
# CLAIM EXTRACTOR AGENT
# ============================================================================

claim_extractor = Agent(
    name="claim_extractor",
    instructions=EXTRACTION_INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ClaimList,
)


# ============================================================================
# METACOGNITIVE ORCHESTRATOR AGENT
# ============================================================================

# ORIGINAL VERBOSE INSTRUCTIONS (commented for potential revert):
# instructions=f"""You are the MetaCheck orchestrator coordinating a fact-checking workflow.
# Your task:
# 1. Use 'claim_extractor' to extract check-worthy claims from input text
# 2. For EACH claim extracted:
#    a. Use 'WebSearchTool' to search the web for evidence
#    b. Use 'wikipedia_search_tool' to search Wikipedia for evidence
#    c. Use 'google_fact_check_tool' to query professional fact-checking databases
#    d. Synthesize ALL evidence and apply VERDICT_CRITERIA to reach a structured verdict
# {VERDICT_CRITERIA}
# {METACOGNITIVE_INSTRUCTIONS}
# For each claim, create VerificationResult with: claim, verdict (SUPPORTED/REFUTED/INSUFFICIENT_INFORMATION/CONFLICTING_EVIDENCE),
# confidence, justification, key_sources with URLs, evidence_list with Evidence objects (source_name, source_type, url, snippet,
# relevance_score, credibility_score, stance). Credibility: fact_check=0.95, wikipedia=0.8, web=0.5-0.85.
# Include actual URLs in all sources. Return OrchestratorOutput with claim_results.
# """

orchestrator = Agent(
    name="metacognitive_orchestrator",
    model=MODEL_NAME,
    model_settings=_model_settings(
        max_completion_tokens=2048,  # Optimized for cost efficiency (was 16384)
        temperature=0.1,  # Lower temperature for more consistent, deterministic factual outputs
    ),
    instructions=f"""Fact-check orchestrator. For each claim:
1. Use comprehensive_evidence_tool to gather ALL evidence (Tavily web search + Wikipedia + Google Fact Check) in parallel
2. comprehensive_evidence_tool returns EvidenceBundle with structured Evidence objects from all three sources
3. For each Evidence object, analyze the snippet content to determine stance:
   - Web search & Wikipedia: Read snippet, set stance to "supports"/"refutes"/"neutral"/"unclear" based on content
   - Fact check: Stance already set correctly by rating interpretation
4. Apply verdict criteria:
   - SUPPORTED: Multiple credible sources (≥0.7) confirm, no contradictions
   - REFUTED: Credible sources (≥0.7) explicitly contradict
   - INSUFFICIENT_INFORMATION: <2 sources OR all <0.7 credibility
   - CONFLICTING_EVIDENCE: Credible sources disagree
5. Return VerificationResult with claim, verdict, confidence (0-1), justification (1-2 sentences), key_sources (format: "Name [url]"), evidence_list with updated stances

CRITICAL: Include actual URLs in key_sources. Evidence is already limited by mode (basic=3+2+2, comprehensive=5+3+3).
""",
    tools=[
        comprehensive_evidence_tool,  # Parallel Tavily + Wikipedia + Fact Check (all-in-one)
        # REVERT TO PARALLEL: Replace line above with these to use wiki_fact_evidence_tool (no Tavily):
        # wiki_fact_evidence_tool,
        # REVERT TO WEBSEARCH: Replace line above with these to use WebSearchTool:
        # WebSearchTool(),
        # wiki_fact_evidence_tool,
    ],
    output_type=OrchestratorOutput,
)



# ============================================================================
# COMPARISON ANALYZER AGENT
# ============================================================================

comparison_analyzer = Agent(
    name="comparison_analyzer",
    model=MODEL_NAME,
    model_settings=_model_settings(
        max_completion_tokens=8192,
        temperature=0.3,  # Slightly creative for engaging feedback
    ),
    instructions="""You are an educational feedback specialist analyzing how a student's fact-checking compares to AI analysis.

Your task:
Analyze the student's claims and verdicts against the AI's extracted claims and verdicts, providing CONCISE educational feedback.

You will receive:
1. Student claims: Each with claim text, verdict, confidence, reasoning, sources, and time spent
2. AI claims: Each with claim text, verdict, confidence, justification, and sources

Provide ONLY these two sections:

1. **overall_summary** (2-3 sentences maximum)
   - Brief high-level assessment of the student's performance
   - Note overall agreement/disagreement patterns
   - Keep it simple and encouraging

2. **areas_for_improvement** (2-4 bullet points, or empty array if performance was strong)
   - Specific, actionable suggestions
   - Focus on the most important improvements only
   - Leave empty if student work was already strong
   - Examples: "Consider checking fact-checking databases for controversial claims", "Source credibility assessment could be strengthened"

Do NOT populate: strengths, key_insights, claim_by_claim_feedback, learning_opportunities, or encouragement fields.

Keep all feedback brief, student-friendly, and focused on actionable insights.""",
    output_type=ComparisonAnalysis,
)
