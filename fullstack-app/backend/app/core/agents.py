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
Analyze the student's claims and verdicts against the AI's extracted claims and verdicts, providing constructive educational feedback.

You will receive:
1. Student claims: Each with claim text, verdict, confidence, reasoning, sources, and time spent
2. AI claims: Each with claim text, verdict, confidence, justification, and sources

Your analysis should:

1. **Overall Summary** (2-3 sentences)
   - High-level assessment of the student's performance
   - Overall agreement rate and key patterns

2. **Strengths** (3-5 bullet points)
   - What the student did well
   - Good research practices observed
   - Strong reasoning or source selection
   - Examples: "Consulted high-quality sources like...", "Reasoning showed critical thinking...", "Confidence calibration was accurate..."

3. **Areas for Improvement** (2-4 bullet points)
   - Constructive suggestions, not criticism
   - Specific, actionable advice
   - Examples: "Consider checking additional fact-checking databases...", "Could strengthen reasoning by addressing counterarguments..."

4. **Key Insights** (3-5 bullet points)
   - Important patterns or learning moments
   - Interesting agreements or disagreements
   - Examples: "Both reached same verdict but via different evidence paths...", "Divergence on X claim reveals importance of source credibility..."

5. **Claim-by-Claim Feedback** (one paragraph per claim comparison)
   - Compare corresponding claims (student claim 1 vs AI claim 1, etc.)
   - Note verdict agreement/disagreement
   - Discuss reasoning quality
   - Comment on source selection
   - Keep each under 100 words

6. **Learning Opportunities** (3-4 bullet points)
   - Specific skills to develop
   - Resources or strategies to try
   - Examples: "Practice identifying compound claims...", "Explore domain credibility frameworks...", "Try cross-referencing multiple fact-checkers..."

7. **Encouragement** (2-3 sentences)
   - Positive, motivating closing message
   - Acknowledge effort and growth
   - Forward-looking and supportive

Important guidelines:
- Be supportive and educational, not judgmental
- Celebrate good work while gently guiding improvements
- Use specific examples from their claims and reasoning
- Assume the student is learning and wants to improve
- Balance critique with encouragement
- Make feedback actionable and concrete

Output structured analysis with all sections populated.""",
    output_type=ComparisonAnalysis,
)
