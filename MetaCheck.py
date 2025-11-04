"""
MetaCheck - Metacognitive Information-Assessment Tool
"""

import asyncio
import os
from datetime import datetime
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
import requests

from agents import Agent, WebSearchTool, Runner, ModelSettings, function_tool

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables.")

# Verify API keys are set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Please set it in .env file or as environment variable.")

if not os.getenv("GOOGLE_FACT_CHECK_API_KEY"):
    print("Warning: GOOGLE_FACT_CHECK_API_KEY not found. Fact-check database queries will be disabled.")

if not os.getenv("WIKIPEDIA_ACCESS_TOKEN"):
    print("Info: WIKIPEDIA_ACCESS_TOKEN not found. Wikipedia API will work without authentication.")


# ============================================================================
# CONSTANTS & CRITERIA
# ============================================================================

VERDICT_CRITERIA = """
Verdict criteria:

SUPPORTED - Use when:
- Multiple credible sources (>=0.7) confirm the claim
- Evidence directly addresses the core assertion
- No credible contradictory evidence
- Sources are authoritative and credible
- Evidence is current/recent enough for time-sensitive claims

REFUTED - Use when:
- Credible sources (>=0.7) explicitly contradict the claim
- Evidence provides clear counter-factual information
- Contradiction is direct and unambiguous
- IMPORTANT: Use REFUTED when high-credibility sources (>0.8) refute the claim, even if low-credibility sources (<0.7) support it

INSUFFICIENT INFORMATION - Use when:
- Very limited evidence (fewer than 2 sources total)
- ALL available sources lack credibility (<0.7)
- Evidence is indirect, vague, or incomplete on ALL sides
- Key information missing for verification
- Evidence is outdated for time-sensitive claims
- IMPORTANT: Do NOT use INSUFFICIENT when credible evidence (>=0.7) clearly refutes or supports the claim, even if some low-credibility sources disagree

CONFLICTING EVIDENCE - Use when:
- Multiple CREDIBLE sources (>=0.7) present opposing views on BOTH sides
- Both supporting and refuting sides have credible evidence
- No clear resolution from available evidence
- Credibility and quantity roughly balanced between both sides
- IMPORTANT: Requires genuine conflict between credible sources, not low-credibility vs credible sources

NEEDS_INSTRUCTOR - Use when:
- Low confidence (<0.6) and contradictions between credible sources
- Sensitive or complex topic requiring expert review
- Evidence is highly technical or specialized

Evidence Weighting Rules:
1. Credibility score thresholds:
   - High-credibility sources: > 0.8 (e.g., fact-checkers at 0.95)
   - Credible sources: >= 0.7 (e.g., Wikipedia at 0.8, web sources 0.70-0.85 from CRAAP test)
   - Low-credibility sources: < 0.7 (unreliable or unclear)

2. Weight evidence by credibility score:
   - High-credibility sources (>0.8) have strongest weight
   - Credible sources (>=0.7) should dominate verdict over low-credibility sources
   - Compare total credibility weight: sum of credibility scores on each side

3. Decision priority:
   - If credible sources (>=0.7) clearly support or refute, use SUPPORTED/REFUTED
   - If credible sources conflict, use CONFLICTING
   - Only use INSUFFICIENT when no credible sources exist or all are unclear
   - Example: 1 high-cred refuting (0.95) outweighs multiple low-cred supporting (0.6, 0.5)

Decision rule: Weight evidence by credibility. Credible sources (>=0.7) dominate verdict decisions.
"""

CRAAP_CRITERIA = """
CRAAP Test Framework for Web Source Credibility Assessment

Assess web sources using the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose).
Each component receives a score from 0.0 to 1.0 based on specific criteria.

=== CURRENCY (Weight: 15%) ===
Evaluate timeliness of the information:

Scoring Guidelines:
- 1.0: Very recent (within 1 year) for time-sensitive topics
- 0.8: Recent (1-2 years)
- 0.6: Moderately recent (2-3 years)
- 0.4: Older (3-5 years)
- 0.2: Very old (5+ years) for time-sensitive topics
- 0.5: No date found (default)

Check URL and snippet for:
- Publication date
- "Updated" or "Last modified" date
- References to current/recent events

Note: For historical facts or timeless information, currency matters less.
For current events or scientific topics, currency is critical.

=== RELEVANCE (Weight: 20%) ===
How well does the source address the specific claim?

Scoring Guidelines:
- 1.0: Directly addresses the exact claim
- 0.8: Addresses the main topic with specific details
- 0.6: Discusses related topic or context
- 0.4: Tangentially related
- 0.2: Barely relevant or off-topic

Indicators:
- Does the snippet mention key terms from the claim?
- Is the focus on the same subject?
- Does it provide specific information about the claim?

=== AUTHORITY (Weight: 30%) - MOST IMPORTANT ===
Source credibility and expertise

Domain Type Baseline Scores:
- government: .gov domains, official agencies (0.85-0.95)
- academic: .edu domains, universities, peer-reviewed journals (0.80-0.90)
- established_news: AP, Reuters, NYT, BBC, WSJ, The Guardian (0.75-0.85)
- medical_institution: Mayo Clinic, Johns Hopkins, CDC, WHO (0.80-0.90)
- fact_checker: Use source_type="fact_check" instead (0.95)
- mainstream: Recognizable news outlets, established organizations (0.65-0.75)
- unknown: Unknown domains, personal blogs, unclear origin (0.50-0.60)
- questionable: Known unreliable sites, extreme bias (0.30-0.45)

Authority Modifiers (apply to baseline):
- Author credentials/expertise mentioned in snippet: +0.05
- Organization clearly identified: +0.05
- No author or organization: -0.10
- Anonymous or unclear source: -0.15

Final authority_score = baseline + modifiers (clipped to 0.0-1.0)

=== ACCURACY (Weight: 25%) ===
Reliability indicators from snippet analysis

Tone Analysis:
- factual: Objective, neutral language (1.0)
- neutral: Mostly objective with minor opinion (0.7)
- sensational: Emotional, exaggerated, ALL CAPS, !!! (0.3)
- biased: Clear bias but not sensational (0.5)
- unclear: Cannot determine from snippet (0.6)

Evidence Indicators (add/subtract from base):
- Snippet mentions sources or citations: +0.15
- Contains specific facts, data, numbers: +0.10
- Technical/scientific terminology used appropriately: +0.10
- Vague claims without specifics: -0.15
- Unverifiable assertions: -0.20
- Contradicts known facts: -0.30

Starting base: 0.7
Apply modifiers based on tone and evidence indicators.
Final accuracy_score clipped to 0.0-1.0.

=== PURPOSE (Weight: 10%) ===
Why does this source exist?

Primary Purpose Assessment:
- inform: Factual reporting, educational content (1.0)
- persuade: Opinion, editorial, advocacy (clearly labeled: 0.7, hidden: 0.4)
- sell: Commercial, sponsored content, advertising (0.4)
- entertain: Satire, humor (if clear: 0.3, if misleading: 0.1)
- mislead: Propaganda, conspiracy, intentional misinformation (0.1-0.2)
- unclear: Cannot determine (0.5)

Bias Indicators (note in bias_indicators field):
- Loaded language: "shocking truth", "they don't want you to know", "exposed"
- One-sided presentation: Only presents one viewpoint
- Emotional appeals: Fear-mongering, outrage, manipulation
- Conspiracy framing: "cover-up", "hidden agenda", unnamed "they"
- Clickbait: Sensational headlines that don't match content

Each bias indicator reduces purpose_score by 0.1 (minimum 0.1)

=== FINAL CALCULATION ===

Step 1: Calculate Overall CRAAP Score
overall_craap_score = (
    (currency_score × 0.15) +
    (relevance_score × 0.20) +
    (authority_score × 0.30) +
    (accuracy_score × 0.25) +
    (purpose_score × 0.10)
)

Step 2: Convert to Credibility Score
credibility_score = clip(overall_craap_score, 0.50, 0.85)

Constraints:
- Web sources maximum: 0.85 (below fact-checkers' fixed 0.95)
- Web sources can score higher than Wikipedia (0.80 fixed) up to 0.85
- Minimum credibility: 0.50 (extremely questionable sources)
- Most web sources: 0.55-0.80 range
- Only professional fact-checkers can exceed 0.85 (they use fixed 0.95)

Step 3: Provide Transparent Reasoning
In the reasoning field, explain:
- Each CRAAP component score and why
- Key factors that influenced the score
- Limitations of the assessment (e.g., no full content access)
- Overall assessment summary

IMPORTANT:
- Be honest about uncertainty - if you can't determine something from the snippet, say so
- Document all assumptions
- Explain scoring rationale clearly
- Note any red flags or concerns
"""

METACOGNITIVE_INSTRUCTIONS = """
EDUCATIONAL TRANSPARENCY REQUIREMENTS:

MetaCheck is designed for students and educators to learn HOW AI evaluates information.
You MUST document your reasoning at EVERY step for educational purposes.

1. QUERY GENERATION PHASE
   Before searching, explicitly document:
   - What query you're generating
   - WHY you chose those specific terms
   - What search strategy you're using (direct/broad/contextual/fact_check)

   Example documentation:
   "Generating query: 'Trump military recruitment 2025'
    Reasoning: Searching for recent sources that directly address the claim using exact terms
    Strategy: direct - using exact keywords from the claim to find specific coverage"

2. EVIDENCE ASSESSMENT PHASE
   For EACH source you find and assess:

   a) For web_search sources:
      - Call craap_assessor and preserve the FULL CRAAPAssessment result
      - Document which CRAAP scores were assigned and why
      - Explain how the CRAAP components led to the final credibility score
      - Note any limitations (e.g., "based on snippet only, full article not accessed")

   b) For ALL sources (web, Wikipedia, fact-check):
      - State explicitly why you marked it as supports/refutes/neutral/unclear
      - Quote specific text from the source that influenced your stance decision
      - Explain the relevance score (how well it addresses the claim)
      - List key factors: publication date, author credentials, organization, etc.

   Example documentation:
   "Source: PolitiFact article
    Stance: REFUTES
    Reasoning: Article provides Pentagon data showing recruitment gains began in August 2024,
               before Trump took office in January 2025
    Key quote: 'The uptick began in August 2024, months before Trump's inauguration'
    Credibility: 0.95 (professional fact-checker with transparent methodology)"

3. VERDICT DECISION PHASE
   Before stating your final verdict, show your complete decision process:

   a) Calculate evidence weights:
      - Sum credibility scores for supporting sources
      - Sum credibility scores for refuting sources
      - Sum credibility scores for neutral sources
      - Show the calculation explicitly

   b) Consider ALL alternative verdicts:
      - List each possible verdict (SUPPORTED, REFUTED, INSUFFICIENT, CONFLICTING, NEEDS_INSTRUCTOR)
      - For each alternative, explain why you selected it OR why you rejected it
      - Identify which specific rule from VERDICT_CRITERIA applies

   c) Identify decisive factors:
      - Which source(s) were most influential in your decision?
      - What was the single most important factor that determined the verdict?
      - If multiple high-credibility sources agree, note this

   d) Explain confidence level:
      - Why this specific confidence score?
      - What factors increased confidence?
      - What factors decreased confidence?

   Example documentation:
   "Evidence Weighting:
    - Supporting: 0 sources, weight = 0.00
    - Refuting: 4 sources, weight = 3.59 (0.95+0.84+0.95+0.85)
    - Neutral: 0 sources, weight = 0.00

    Verdict Alternatives Considered:
    - SUPPORTED: Rejected (no supporting evidence exists)
    - REFUTED: SELECTED (unanimous high-credibility refuting evidence)
    - CONFLICTING: Rejected (requires credible sources on BOTH sides, we only have refuting)
    - INSUFFICIENT: Rejected (we have 4 high-credibility sources, not insufficient)

    Decisive Factor: Three independent fact-checkers all agree using Pentagon data
    Confidence: 0.88 (high credibility sources, unanimous agreement, specific data)"

4. UNCERTAINTY ACKNOWLEDGMENT
   Be transparent about what you DON'T know:

   - What information was unavailable?
     Example: "Only accessed snippets, not full articles"

   - What assumptions did you make?
     Example: "Assumed professional fact-checkers (0.95) are most credible tier"

   - Where might this assessment be wrong?
     Example: "Only reviewed 4 of 10+ sources found; more sources might provide different context"

   - What would improve this assessment?
     Example: "Access to full Pentagon recruitment data would provide independent verification"

5. METACOGNITIVE DETAIL POPULATION
   You MUST populate the metacognitive_detail field in VerificationResult with:

   - search_queries: List all SearchQuery objects with reasoning
   - sources_assessed: List all SourceAssessment objects with full details
   - verdict_reasoning: Complete VerdictReasoning with alternatives and decisive factors
   - ai_uncertainties: What you couldn't determine
   - assumptions_made: What assumptions were necessary
   - potential_weaknesses: Where the assessment could be wrong

REMEMBER: Students learn more from seeing your reasoning process than from your final answer.
Show your work. Explain your thinking. Acknowledge uncertainty. Be educational, not just accurate.
"""


# ============================================================================
# ENHANCED DATA MODELS
# ============================================================================

class Claim(BaseModel):
    """A single factual claim extracted from text"""
    text: str
    worthiness_score: float = Field(ge=0.0, le=1.0, default=0.8)
    extracted_at: datetime = Field(default_factory=datetime.now)


class ClaimList(BaseModel):
    """List of extracted claims"""
    claims: List[Claim]
    extraction_method: str = "AI claim extractor"


class Evidence(BaseModel):
    """A single piece of evidence from a source"""
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.7)
    credibility_score: float = Field(ge=0.0, le=1.0, default=0.7)
    stance: Optional[Literal["supports", "refutes", "neutral", "unclear"]] = None


class MetacognitiveStep(BaseModel):
    """A step in the metacognitive reasoning process"""
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str
    action: str
    reasoning: str
    confidence: Optional[float] = None


class VerificationResult(BaseModel):
    """Result of verifying a single claim - Enhanced with full metacognitive detail"""
    claim: str
    verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str
    key_sources: List[str]  # Format: "Source Name [URL]"
    evidence_list: List[Evidence] = []
    metacognitive_steps: List[MetacognitiveStep] = []

    # NEW: Enhanced metacognitive details for educational transparency
    metacognitive_detail: Optional['MetacognitiveDetail'] = None


class FinalAssessment(BaseModel):
    """Final assessment of all claims"""
    input_text: str
    total_claims: int
    claim_results: List[VerificationResult]
    overall_credibility: str
    generated_at: datetime = Field(default_factory=datetime.now)


class ContradictionDetection(BaseModel):
    """Detection of contradictory evidence"""
    detected: bool = False
    contradicting_sources: List[str] = []
    description: str = ""
    severity: Literal["minor", "moderate", "major"] = "minor"


class EscalationDecision(BaseModel):
    """Decision on whether to escalate to instructor"""
    should_escalate: bool
    reasons: List[str]
    instructor_notes: str
    suggested_actions: List[str] = []


class SensitivityAnalysis(BaseModel):
    """LLM-based analysis of claim sensitivity"""
    is_sensitive: bool
    sensitive_categories: List[str] = []  # e.g., ["health", "medical"], or empty if not sensitive
    reasoning: str = ""


class CRAAPAssessment(BaseModel):
    """CRAAP test evaluation for web sources (Currency, Relevance, Authority, Accuracy, Purpose)"""

    # Currency (0.0-1.0)
    currency_score: float = Field(ge=0.0, le=1.0)
    currency_notes: str
    has_date: bool = False
    is_recent: Optional[bool] = None  # True if within 2 years, False if older, None if unknown

    # Relevance (0.0-1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_notes: str
    addresses_claim: Literal["directly", "partially", "tangentially", "unclear"]

    # Authority (0.0-1.0)
    authority_score: float = Field(ge=0.0, le=1.0)
    authority_notes: str
    domain_type: Literal["government", "academic", "established_news", "medical_institution",
                         "fact_checker", "mainstream", "unknown", "questionable"]
    author_mentioned: bool = False
    organization_clear: bool = False

    # Accuracy (0.0-1.0)
    accuracy_score: float = Field(ge=0.0, le=1.0)
    accuracy_notes: str
    cites_sources: bool = False
    tone: Literal["factual", "neutral", "sensational", "biased", "unclear"]
    verifiable_claims: bool = False

    # Purpose (0.0-1.0)
    purpose_score: float = Field(ge=0.0, le=1.0)
    purpose_notes: str
    primary_purpose: Literal["inform", "persuade", "sell", "entertain", "mislead", "unclear"]
    bias_indicators: List[str] = []  # e.g., ["loaded language", "one-sided"]

    # Overall
    overall_craap_score: float = Field(ge=0.0, le=1.0)  # Weighted average
    credibility_score: float = Field(ge=0.5, le=0.85)  # Final score for MetaCheck (clipped to 0.5-0.85)
    reasoning: str  # Summary explanation


class SearchQuery(BaseModel):
    """Record of search queries generated by the AI for educational transparency"""
    query_text: str
    query_reasoning: str  # WHY this query was generated
    search_strategy: Literal["direct", "broad", "contextual", "fact_check"]
    source_tool: Literal["WebSearchTool", "wikipedia_search_tool", "google_fact_check_tool"]
    timestamp: datetime = Field(default_factory=datetime.now)
    results_count: int = 0
    results_used: int = 0  # How many results were actually assessed


class SourceAssessment(BaseModel):
    """Detailed assessment of a single source for educational transparency"""
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    title: str = ""

    # CRAAP details (only for web_search)
    craap_assessment: Optional[CRAAPAssessment] = None

    # Relevance
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_reasoning: str  # WHY this relevance score?
    relevance_factors: List[str] = []  # ["directly addresses claim", "contains key terms"]

    # Stance
    stance: Literal["supports", "refutes", "neutral", "unclear"]
    stance_reasoning: str  # WHY this stance?
    key_quotes: List[str] = []  # Quotes that influenced stance determination

    # Credibility
    credibility_score: float = Field(ge=0.0, le=1.0)
    credibility_reasoning: str  # HOW was this score determined?
    credibility_factors: List[str] = []  # ["professional fact-checker", "recent publication"]

    # Content
    snippet: str
    full_text_available: bool = False
    publication_date: Optional[str] = None
    author: Optional[str] = None


class VerdictReasoning(BaseModel):
    """Detailed reasoning for verdict decision - educational transparency"""
    final_verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float = Field(ge=0.0, le=1.0)

    # Evidence weighting calculation
    supporting_sources_count: int
    supporting_weight: float  # Sum of credibility scores
    supporting_key_sources: List[str] = []  # Names of key supporting sources

    refuting_sources_count: int
    refuting_weight: float  # Sum of credibility scores
    refuting_key_sources: List[str] = []  # Names of key refuting sources

    neutral_sources_count: int
    neutral_weight: float

    unclear_sources_count: int

    # Decision logic
    primary_reason: str  # Main reason for this verdict
    decision_rule_applied: str  # Which rule from VERDICT_CRITERIA was applied

    # Alternatives considered
    alternative_verdicts_considered: List[str] = []  # e.g., ["CONFLICTING", "INSUFFICIENT"]
    why_not_alternatives: str = ""  # Why alternatives were rejected

    # Decisive factors
    decisive_sources: List[str] = []  # Which sources tipped the decision
    decisive_factor: str  # What ultimately determined the verdict

    # Confidence calculation
    confidence_reasoning: str  # Why this confidence level
    confidence_factors: List[str] = []  # ["high source credibility", "unanimous agreement"]


class RejectedSource(BaseModel):
    """A source that was found but rejected from analysis"""
    url: str
    reason: str



class MetacognitiveDetail(BaseModel):
    """Complete metacognitive record for one claim - full educational transparency"""
    claim: str

    # Phase 1: Query Generation
    search_queries: List[SearchQuery] = []
    search_strategy_summary: str = ""

    # Phase 2: Evidence Collection
    sources_found: int = 0
    sources_assessed: List[SourceAssessment] = []
    sources_rejected: List[RejectedSource] = []  # Sources found but not used, with reasons

    # Phase 3: Evidence Analysis
    contradiction_detection: Optional[ContradictionDetection] = None
    verdict_reasoning: Optional[VerdictReasoning] = None

    # Phase 4: Meta-analysis
    sensitivity_analysis: Optional[SensitivityAnalysis] = None
    escalation_decision: Optional[EscalationDecision] = None

    # Phase 5: Limitations & Uncertainties
    ai_uncertainties: List[str] = []  # What the AI couldn't determine
    assumptions_made: List[str] = []  # Assumptions in the assessment
    potential_weaknesses: List[str] = []  # Where this assessment might be wrong

    # Overall
    total_assessment_time: Optional[float] = None  # Seconds
    metacognitive_summary: str = ""  # High-level summary for students


class OrchestratorOutput(BaseModel):
    """Structured output from the orchestrator with all verified claims"""
    claim_results: List[VerificationResult]
    summary: str = ""


# ============================================================================
# METACOGNITIVE LAYER - PHASE 2
# ============================================================================

class MetacognitiveTracker:
    """
    Tracks reasoning steps, assesses confidence, and detects contradictions.
    Provides transparency into the fact-checking process.
    """

    def __init__(self):
        self.steps: List[MetacognitiveStep] = []
        self.evidence_collected: List[Evidence] = []

    def add_step(self, agent: str, action: str, reasoning: str, confidence: Optional[float] = None):
        """Add a reasoning step to the tracking history"""
        step = MetacognitiveStep(
            timestamp=datetime.now(),
            agent=agent,
            action=action,
            reasoning=reasoning,
            confidence=confidence
        )
        self.steps.append(step)

    def add_evidence(self, evidence: Evidence):
        """Track collected evidence"""
        self.evidence_collected.append(evidence)

    def assess_confidence(self, verdict: str, evidence_list: List[Evidence]) -> float:
        """
        Assess confidence based on evidence quality and quantity.

        Confidence scale:
        - High (0.8-1.0): 3+ authoritative sources agree
        - Medium (0.5-0.8): Some evidence but incomplete
        - Low (0-0.5): Contradictory or insufficient
        """
        if not evidence_list:
            return 0.0

        # Count evidence by stance
        supporting = sum(1 for e in evidence_list if e.stance == "supports")
        refuting = sum(1 for e in evidence_list if e.stance == "refutes")
        neutral = sum(1 for e in evidence_list if e.stance == "neutral")
        unclear = sum(1 for e in evidence_list if e.stance == "unclear")

        # Count high-credibility sources (>0.8: fact-checkers 0.95, Wikipedia 0.8)
        authoritative_sources = sum(1 for e in evidence_list if e.credibility_score >= 0.8)

        # Base confidence on verdict alignment
        if verdict == "SUPPORTED":
            if supporting >= 3 and authoritative_sources >= 2:
                base_confidence = 0.9
            elif supporting >= 2:
                base_confidence = 0.7
            else:
                base_confidence = 0.5

        elif verdict == "REFUTED":
            if refuting >= 3 and authoritative_sources >= 2:
                base_confidence = 0.9
            elif refuting >= 2:
                base_confidence = 0.7
            else:
                base_confidence = 0.5

        elif verdict == "CONFLICTING":
            # Conflicting evidence means lower confidence
            base_confidence = 0.4

        elif verdict == "INSUFFICIENT":
            base_confidence = 0.3

        else:  # NEEDS_INSTRUCTOR
            base_confidence = 0.2

        # Adjust based on evidence credibility
        avg_credibility = sum(e.credibility_score for e in evidence_list) / len(evidence_list)
        confidence = (base_confidence + avg_credibility) / 2

        return min(1.0, max(0.0, confidence))

    def detect_contradictions(self, evidence_list: List[Evidence]) -> ContradictionDetection:
        """
        Detect contradictory evidence and assess severity.

        Uses tiered credibility thresholds:
        - Credible sources: >= 0.7 (fact-checkers 0.95, Wikipedia 0.8, web_search 0.50-0.85 from CRAAP)
        - Moderate credibility: 0.5 to < 0.7 (less authoritative but still relevant)
        - Low credibility: < 0.5 (unreliable, ignored in contradiction detection)
        """
        supporting = [e for e in evidence_list if e.stance == "supports"]
        refuting = [e for e in evidence_list if e.stance == "refutes"]

        if len(supporting) == 0 or len(refuting) == 0:
            return ContradictionDetection(detected=False)

        # Count credible (>=0.7) and moderate-credibility (0.5-0.7) sources
        credible_supporting = [e for e in supporting if e.credibility_score >= 0.7]
        credible_refuting = [e for e in refuting if e.credibility_score >= 0.7]

        moderate_cred_supporting = [e for e in supporting if 0.5 <= e.credibility_score < 0.7]
        moderate_cred_refuting = [e for e in refuting if 0.5 <= e.credibility_score < 0.7]

        # Total sources with at least moderate credibility (>=0.5)
        all_supporting = credible_supporting + moderate_cred_supporting
        all_refuting = credible_refuting + moderate_cred_refuting

        # Check if we have any contradiction (even with moderate credibility)
        if len(all_supporting) > 0 and len(all_refuting) > 0:
            # We have contradictory evidence
            contradicting_sources = [
                f"{e.source_name} (supports, cred={e.credibility_score:.2f})" for e in all_supporting
            ] + [
                f"{e.source_name} (refutes, cred={e.credibility_score:.2f})" for e in all_refuting
            ]

            # Assess severity based on both quantity and credibility
            # Major: Multiple credible sources (>=0.7) on both sides
            if len(credible_supporting) >= 2 and len(credible_refuting) >= 2:
                severity = "major"
                description = f"Found {len(credible_supporting)} credible sources (>=0.7) supporting and {len(credible_refuting)} credible sources refuting the claim."

            # Moderate: Credible sources on both sides, or many total sources
            elif len(credible_supporting) >= 1 and len(credible_refuting) >= 1:
                severity = "moderate"
                description = f"Found {len(all_supporting)} sources supporting (credible >=0.7: {len(credible_supporting)}) and {len(all_refuting)} sources refuting (credible >=0.7: {len(credible_refuting)}) the claim."

            # Moderate: Mix of moderate and credible sources with multiple total
            elif len(all_supporting) + len(all_refuting) >= 3:
                severity = "moderate"
                description = f"Found {len(all_supporting)} sources supporting and {len(all_refuting)} sources refuting the claim."

            # Minor: Only a few sources or only moderate credibility
            else:
                severity = "minor"
                description = f"Found {len(all_supporting)} sources supporting and {len(all_refuting)} sources refuting the claim (some with moderate credibility 0.5-0.7)."

            return ContradictionDetection(
                detected=True,
                contradicting_sources=contradicting_sources,
                description=description,
                severity=severity
            )

        return ContradictionDetection(detected=False)

    def get_reasoning_path(self) -> str:
        """Generate a human-readable reasoning path"""
        if not self.steps:
            return "No reasoning steps recorded."

        path = "Reasoning Path:\n"
        for i, step in enumerate(self.steps, 1):
            path += f"\n{i}. [{step.agent}] {step.action}\n"
            path += f"   Reasoning: {step.reasoning}\n"
            if step.confidence is not None:
                path += f"   Confidence: {step.confidence:.2f}\n"

        return path


class EscalationManager:
    """
    Manages escalation decisions and generates instructor notes.
    Determines when claims need expert human review.

    Note: Sensitivity detection is now LLM-based, not hard-coded keywords.
    """

    # Escalation thresholds
    CONFIDENCE_THRESHOLD = 0.6

    def should_escalate(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        contradiction: ContradictionDetection,
        evidence_list: List[Evidence],
        sensitivity_analysis: SensitivityAnalysis = None
    ) -> EscalationDecision:
        """
        Determine if a claim should be escalated to an instructor.

        Escalation criteria:
        - Low confidence (< 0.6) AND (contradictions OR sensitive topic)
        - Major contradictions from authoritative sources
        - NEEDS_INSTRUCTOR verdict
        - Sensitive topic identified by LLM analysis
        """
        reasons = []
        should_escalate = False

        # Check for NEEDS_INSTRUCTOR verdict
        if verdict == "NEEDS_INSTRUCTOR":
            should_escalate = True
            reasons.append("Verdict explicitly marked as NEEDS_INSTRUCTOR")

        # Check low confidence with contradictions
        if confidence < self.CONFIDENCE_THRESHOLD:
            if contradiction.detected:
                should_escalate = True
                reasons.append(f"Low confidence ({confidence:.2f}) combined with contradictory evidence")

            # Check for sensitive topics using LLM analysis
            if sensitivity_analysis and sensitivity_analysis.is_sensitive:
                should_escalate = True
                categories_str = ", ".join(sensitivity_analysis.sensitive_categories) if sensitivity_analysis.sensitive_categories else "general"
                reasons.append(f"Low confidence ({confidence:.2f}) on sensitive topic ({categories_str})")

        # Check for major contradictions regardless of confidence
        if contradiction.detected and contradiction.severity == "major":
            should_escalate = True
            reasons.append(f"Major contradictions detected between credible sources")

        # Check for insufficient evidence on important claims
        if verdict == "INSUFFICIENT" and len(evidence_list) < 2:
            if sensitivity_analysis and sensitivity_analysis.is_sensitive:
                should_escalate = True
                reasons.append("Insufficient evidence for sensitive claim")

        # Generate instructor notes
        instructor_notes = self._generate_instructor_notes(
            claim, verdict, confidence, contradiction, evidence_list, reasons
        )

        # Suggest actions
        suggested_actions = self._suggest_actions(verdict, contradiction, evidence_list)

        return EscalationDecision(
            should_escalate=should_escalate,
            reasons=reasons,
            instructor_notes=instructor_notes,
            suggested_actions=suggested_actions
        )

    def _generate_instructor_notes(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        contradiction: ContradictionDetection,
        evidence_list: List[Evidence],
        reasons: List[str]
    ) -> str:
        """Generate comprehensive notes for instructor review"""
        notes = f"INSTRUCTOR REVIEW NEEDED\n"
        notes += f"{'='*60}\n\n"
        notes += f"Claim: {claim}\n\n"
        notes += f"Automated Verdict: {verdict}\n"
        notes += f"Confidence: {confidence:.2f}\n\n"

        if reasons:
            notes += "Escalation Reasons:\n"
            for reason in reasons:
                notes += f"  - {reason}\n"
            notes += "\n"

        if contradiction.detected:
            notes += f"Contradiction Analysis:\n"
            notes += f"  Severity: {contradiction.severity.upper()}\n"
            notes += f"  {contradiction.description}\n"
            notes += f"  Contradicting sources:\n"
            for source in contradiction.contradicting_sources:
                notes += f"    - {source}\n"
            notes += "\n"

        notes += f"Evidence Summary:\n"
        notes += f"  Total sources: {len(evidence_list)}\n"

        by_type = {}
        for e in evidence_list:
            by_type[e.source_type] = by_type.get(e.source_type, 0) + 1
        for source_type, count in by_type.items():
            notes += f"  - {source_type}: {count}\n"

        return notes

    def _suggest_actions(
        self,
        verdict: str,
        contradiction: ContradictionDetection,
        evidence_list: List[Evidence]
    ) -> List[str]:
        """Suggest actions for instructor"""
        actions = []

        if contradiction.detected:
            actions.append("Review contradictory sources directly for nuance")
            actions.append("Consult domain experts if needed")

        if verdict == "INSUFFICIENT":
            actions.append("Conduct additional manual research")
            actions.append("Consider specialized databases or academic sources")

        if verdict == "CONFLICTING":
            actions.append("Analyze methodology and bias of conflicting sources")
            actions.append("Determine if conflict is due to different interpretations")

        actions.append("Provide students with reasoning for final determination")

        return actions


# ============================================================================
# GOOGLE FACT CHECK API CLIENT
# ============================================================================

class GoogleFactCheckClient:
    """Client for Google Fact Check Tools API"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def search_fact_checks(self, query: str, language_code: str = "en", max_results: int = 5) -> List[Evidence]:
        """
        Search for fact-checks related to a query.
        Returns list of Evidence objects from professional fact-checkers.
        """
        if not self.api_key:
            return []

        try:
            params = {
                "query": query,
                "languageCode": language_code,
                "key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            claims = data.get("claims", [])
            evidence_list = []

            for claim in claims[:max_results]:
                review = claim.get("claimReview", [{}])[0]
                publisher = review.get("publisher", {})

                evidence = Evidence(
                    source_name=publisher.get("name", "Unknown Fact-Checker"),
                    source_type="fact_check",
                    url=review.get("url", ""),
                    snippet=f"{claim.get('text', '')[:200]}... Rating: {review.get('textualRating', 'N/A')}",
                    relevance_score=0.9,  # Fact-checks are highly relevant
                    credibility_score=0.95,  # Professional fact-checkers are highly credible
                    stance=self._interpret_rating(review.get("textualRating", ""))
                )
                evidence_list.append(evidence)

            return evidence_list

        except requests.RequestException as e:
            print(f"Google Fact Check API error: {e}")
            return []

    def _interpret_rating(self, rating: str) -> Literal["supports", "refutes", "neutral", "unclear"]:
        """Interpret fact-checker rating"""
        rating_lower = rating.lower()
        if any(word in rating_lower for word in ["false", "incorrect", "misleading", "pants on fire"]):
            return "refutes"
        elif any(word in rating_lower for word in ["true", "correct", "accurate"]):
            return "supports"
        elif any(word in rating_lower for word in ["mixture", "mixed", "partly"]):
            return "neutral"
        else:
            return "unclear"


# ============================================================================
# WIKIPEDIA API CLIENT
# ============================================================================

class WikipediaClient:
    """Client for Wikipedia REST API"""

    def __init__(self):
        self.access_token = os.getenv("WIKIPEDIA_ACCESS_TOKEN")
        self.search_url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
        self.summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self.headers = {
            "User-Agent": "MetaCheck/1.0 (Educational Tool)",
        }
        if self.access_token:
            self.headers["Authorization"] = f"Bearer {self.access_token}"

    def search_pages(self, query: str, limit: int = 5) -> List[dict]:
        """Search Wikipedia pages"""
        try:
            response = requests.get(
                self.search_url,
                params={"q": query, "limit": limit},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("pages", [])
        except requests.RequestException as e:
            print(f"Wikipedia search error: {e}")
            return []

    def get_summary(self, title: str) -> Optional[dict]:
        """Get page summary"""
        try:
            response = requests.get(
                self.summary_url + requests.utils.quote(title),
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Wikipedia summary error: {e}")
            return None

    def search_for_claim(self, claim: str, max_results: int = 3) -> List[Evidence]:
        """
        Search Wikipedia for information related to a claim.
        Returns list of Evidence objects.
        """
        pages = self.search_pages(claim, limit=max_results)
        evidence_list = []

        for page in pages:
            title = page.get("title", "")
            summary = self.get_summary(title)

            if summary:
                evidence = Evidence(
                    source_name=f"Wikipedia: {title}",
                    source_type="wikipedia",
                    url=summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    snippet=summary.get("extract", "")[:300],
                    relevance_score=0.7,
                    credibility_score=0.8,  # Wikipedia is generally credible but community-edited
                    stance="neutral"  # Wikipedia aims for neutral POV
                )
                evidence_list.append(evidence)

        return evidence_list


# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

extraction_instructions = """
You are a claim extractor who has expertise in extracting verifiable claims from contents.
Use a moderate approach to extract only those claims which warrant exploring different fact checking sources for verification.
Do not extract well-known facts as claims.
Return a list of extracted claims in structured format.
"""

retriever_instructions = f"""You are an expert research agent for gathering evidence about factual claims.

Your task:
1. Use web search to find relevant, authoritative sources
2. Prioritize recent, credible sources (news outlets, academic sites, government sites)
3. Look for both supporting and refuting evidence
4. Return comprehensive evidence with source URLs

For each piece of evidence, assess:
- Relevance to the claim
- Credibility of the source
- Whether it supports, refutes, or is neutral regarding the claim

{VERDICT_CRITERIA}
"""

fact_check_instructions = """You are a fact-checking specialist agent.

Your task:
1. Query professional fact-checking databases for existing fact-checks
2. Prioritize fact-checks from established organizations (Snopes, PolitiFact, FactCheck.org, etc.)
3. Report findings with source URLs and ratings
4. Note: Professional fact-checkers have already verified these claims

Return all fact-check results found, even if they conflict.
"""

verifier_instructions = f"""You are an expert verification and explanation agent.

Your task:
1. Synthesize ALL evidence provided (from web search, Wikipedia, fact-checkers)
2. Weigh evidence by source credibility and relevance
3. Apply the verdict criteria systematically
4. Provide clear justification for your verdict
5. List all key sources used in format: "Source Name [URL]"

{VERDICT_CRITERIA}

Important:
- Be transparent about confidence level
- Acknowledge contradictions if present
- Recommend instructor review if confidence is low (<0.6) or topic is sensitive
"""

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# External API clients (used as tools)
google_fact_check_client = GoogleFactCheckClient()
wikipedia_client = WikipediaClient()


# 1. Claim Extractor Agent
claim_extractor = Agent(
    name="claim_extractor",
    instructions=extraction_instructions,
    output_type=ClaimList,
)


# 1b. Sensitivity Analyzer Agent
sensitivity_analyzer = Agent(
    name="sensitivity_analyzer",
    instructions="""You are a sensitivity analysis expert who determines if a claim involves sensitive topics.

Your task:
1. Analyze the claim for sensitive content
2. Determine if it relates to any sensitive categories
3. Provide reasoning for your determination

Consider these common sensitive categories (but use your judgment):
- Health & Medical: Disease, treatment, medication, vaccines, diagnosis, mortality
- Safety & Security: Violence, crime, terrorism, weapons, threats
- Vulnerable Populations: Children, minors, elderly, abuse, exploitation
- Political: Elections, voting, fraud, government actions
- Legal: Court cases, allegations, investigations
- Financial: Scams, fraud, investment risks
- Religious: Sacred beliefs, religious figures
- Identity: Race, ethnicity, gender, sexuality (when used divisively)

IMPORTANT:
- Use your judgment - not all mentions of these topics are sensitive
- Context matters: "vaccines are effective" vs "vaccines cause autism" have different sensitivity
- Focus on claims that could cause harm if misinformation spreads
- If no sensitive elements exist, output is_sensitive=False with empty categories list

Output structured analysis with clear reasoning.""",
    output_type=SensitivityAnalysis,
)


# 1c. CRAAP Assessor Agent
craap_assessor = Agent(
    name="craap_assessor",
    instructions=f"""You are a web source credibility assessor using the CRAAP test framework.

{CRAAP_CRITERIA}

Your task:
1. Receive a web source (URL, title, snippet) and the claim it relates to
2. Assess the source using all five CRAAP components
3. Calculate weighted scores
4. Provide transparent reasoning for all assessments

Input format:
- url: The web source URL
- title: Article/page title
- snippet: Brief excerpt from the source (usually ~200 characters)
- claim: The claim being fact-checked (for relevance assessment)

IMPORTANT:
- Be systematic - evaluate ALL five CRAAP components
- Be transparent - explain each score clearly
- Be honest - if you can't determine something from limited info, say so and use default scores
- Be consistent - apply the same standards to all sources
- Follow the scoring guidelines precisely
- The final credibility_score must be clipped to [0.50, 0.85] range

Output a complete CRAAPAssessment with all required fields.""",
    output_type=CRAAPAssessment,
)


# 2. Retriever Agent (Web + Wikipedia)
@function_tool
def wikipedia_search_tool(claim: str) -> str:
    """
    Retrieve evidence from Wikipedia.

    Args:
        claim: The factual claim to search for

    Returns:
        Formatted string with Wikipedia evidence
    """
    evidence = wikipedia_client.search_for_claim(claim, max_results=2)

    if not evidence:
        return "No Wikipedia evidence found."

    result = f"Retrieved {len(evidence)} pieces of Wikipedia evidence:\n\n"
    for i, ev in enumerate(evidence, 1):
        result += f"{i}. {ev.source_name}\n"
        result += f"   URL: {ev.url}\n"
        result += f"   Snippet: {ev.snippet}\n"
        result += f"   Credibility: {ev.credibility_score}\n\n"

    return result


retriever_agent = Agent(
    name="retriever_agent",
    instructions=retriever_instructions,
    tools=[WebSearchTool(), wikipedia_search_tool],
)


# 3. Fact-Check Agent
@function_tool
def google_fact_check_tool(claim: str) -> str:
    """
    Query Google Fact Check API for professional fact-checks.

    Args:
        claim: The factual claim to fact-check

    Returns:
        Formatted string with fact-check results
    """
    evidence = google_fact_check_client.search_fact_checks(claim, max_results=5)

    if not evidence:
        return "No professional fact-checks found for this claim."

    result = f"Found {len(evidence)} professional fact-checks:\n\n"
    for i, ev in enumerate(evidence, 1):
        result += f"{i}. {ev.source_name}\n"
        result += f"   URL: {ev.url}\n"
        result += f"   Assessment: {ev.snippet}\n"
        result += f"   Stance: {ev.stance}\n\n"

    return result


fact_check_agent = Agent(
    name="fact_check_agent",
    instructions=fact_check_instructions,
    tools=[google_fact_check_tool],
)


# 4. Verifier/Explainer Agent
verifier_agent = Agent(
    name="verifier_agent",
    instructions=verifier_instructions,
    output_type=VerificationResult,
)


# 5. Metacognitive Orchestrator (with direct access to all tools)
orchestrator = Agent(
    name="metacognitive_orchestrator",
    instructions=f"""You are the MetaCheck orchestrator coordinating a fact-checking workflow.

Your task:
1. Use 'claim_extractor' to extract check-worthy claims from input text
2. For EACH claim extracted:
   a. Use 'WebSearchTool' to search the web for evidence
   b. For EACH web_search result, use 'craap_assessor' to assess credibility using CRAAP test
   c. Use 'wikipedia_search_tool' to search Wikipedia for evidence
   d. Use 'google_fact_check_tool' to query professional fact-checking databases
   e. Synthesize ALL evidence and apply VERDICT_CRITERIA to reach a structured verdict

{VERDICT_CRITERIA}

{METACOGNITIVE_INSTRUCTIONS}

For each claim, you MUST create a VerificationResult with:
- claim: The exact claim text (string)
- verdict: MUST be one of [SUPPORTED, REFUTED, INSUFFICIENT, CONFLICTING, NEEDS_INSTRUCTOR]
- confidence: Float between 0.0 and 1.0
- justification: Clear reasoning explaining the verdict
- key_sources: List of sources with ACTUAL URLs from tool results in format "Source Name [https://actual-url.com]"
  CRITICAL: Extract the real URLs from WebSearchTool, wikipedia_search_tool, and google_fact_check_tool outputs
  Example: "CDC Vaccine Facts [https://www.cdc.gov/vaccines]" NOT "CDC Vaccine Facts [source]"
- evidence_list: MUST be populated with Evidence objects from tool results
  CRITICAL: For EACH piece of evidence from tools, create an Evidence object with:
    * source_name: Name of the source (e.g., "CDC", "Wikipedia: COVID-19", "Snopes")
    * source_type: "web_search" (from WebSearchTool), "wikipedia" (from wikipedia_search_tool), or "fact_check" (from google_fact_check_tool)
    * url: The actual URL from the tool result
    * snippet: A brief excerpt or description (max 300 characters)
    * relevance_score: 0.0-1.0 (how relevant to the claim)
    * credibility_score: 0.0-1.0 based on source type:
      - fact_check: FIXED 0.95 (professional fact-checkers)
      - wikipedia: FIXED 0.8 (Wikipedia sources)
      - web_search: Use credibility_score from craap_assessor CRAAPAssessment (CRAAP test evaluation, range 0.50-0.85)
    * stance: "supports", "refutes", "neutral", or "unclear"

  WORKFLOW for web_search sources:
  1. Get web search results from WebSearchTool
  2. For EACH result, call craap_assessor with:
     - url: the URL from web search
     - title: the title from web search
     - snippet: the snippet/description from web search
     - claim: the claim being fact-checked
  3. Extract credibility_score from CRAAPAssessment output
  4. Create Evidence object using that credibility_score

  Example for web_search: Evidence(source_name="CDC", source_type="web_search", url="https://www.cdc.gov/...", snippet="Vaccines are safe...", relevance_score=0.9, credibility_score=0.78, stance="supports")
  Example for wikipedia: Evidence(source_name="Wikipedia: COVID-19", source_type="wikipedia", url="https://en.wikipedia.org/...", snippet="COVID-19 is...", relevance_score=0.95, credibility_score=0.8, stance="supports")
  Example for fact_check: Evidence(source_name="Snopes", source_type="fact_check", url="https://www.snopes.com/...", snippet="Claim is false...", relevance_score=1.0, credibility_score=0.95, stance="refutes")
- metacognitive_steps: Can be empty list []

Metacognitive awareness:
- Track confidence for each step
- Note when evidence is contradictory
- Recommend NEEDS_INSTRUCTOR verdict for low-confidence (<0.6) or sensitive claims
- Be transparent about reasoning process

CRITICAL REQUIREMENTS:
- Verify EVERY claim individually
- Use ALL available tools for comprehensive evidence gathering
- Apply VERDICT_CRITERIA systematically
- Include ACTUAL URLs (not placeholders like [source]) from all tool results in key_sources
- Return structured OrchestratorOutput with claim_results containing ALL VerificationResult objects
""",
    tools=[
        claim_extractor.as_tool(
            tool_name="claim_extractor",
            tool_description="Extract verifiable claims from text. Returns a list of claims."
        ),
        WebSearchTool(),
        craap_assessor.as_tool(
            tool_name="craap_assessor",
            tool_description="Assess web source credibility using CRAAP test. Input: url, title, snippet, claim. Returns CRAAPAssessment with credibility_score (0.50-0.85)."
        ),
        wikipedia_search_tool,
        google_fact_check_tool,
    ],
    output_type=OrchestratorOutput,
)


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

async def verify_claims(text: str, verbose: bool = True) -> FinalAssessment:
    """
    Main MetaCheck workflow with Phase 2 metacognitive layer.

    Args:
        text: Input text to analyze
        verbose: Print progress information

    Returns:
        FinalAssessment with all results and metacognitive analysis
    """
    if verbose:
        print(f"\n{'='*70}")
        print("MetaCheck - Metacognitive Information Assessment (Phase 2)")
        print(f"{'='*70}\n")
        print(f"Analyzing text: {text[:100]}...\n")

    # Initialize metacognitive tracking
    tracker = MetacognitiveTracker()
    escalation_mgr = EscalationManager()

    # Track workflow start
    tracker.add_step(
        agent="MetaCheck_System",
        action="Workflow initiated",
        reasoning=f"Beginning fact-check analysis of {len(text)} character input",
        confidence=1.0
    )

    # Run orchestrator to coordinate entire workflow
    tracker.add_step(
        agent="Orchestrator",
        action="Coordinating multi-agent fact-checking",
        reasoning="Extracting claims and gathering evidence from multiple sources"
    )

    result = await Runner.run(
        orchestrator,
        f"Analyze this text and fact-check all claims with full metacognitive transparency: {text}",
        max_turns=30  # Allow enough turns for multiple claims with multiple tool calls each
    )

    # Get structured output from orchestrator
    orchestrator_output: OrchestratorOutput = result.final_output
    claim_results = orchestrator_output.claim_results

    if verbose:
        print(f"\n{'='*70}")
        print("FACT-CHECKING REPORT")
        print(f"{'='*70}\n")

        # Display results from structured output
        for i, claim_result in enumerate(claim_results, 1):
            print(f"\n## Claim {i}")
            print(f"**Claim:** {claim_result.claim}")
            print(f"\n**Verdict:** {claim_result.verdict}")
            print(f"**Confidence:** {claim_result.confidence:.2f}")
            print(f"\n**Justification:** {claim_result.justification}")
            if claim_result.key_sources:
                print(f"\n**Key Sources:**")
                for source in claim_result.key_sources:
                    print(f"  - {source}")
            print(f"\n{'-'*70}")

    # Track completion
    tracker.add_step(
        agent="Orchestrator",
        action="Fact-checking completed",
        reasoning=f"Analyzed {len(claim_results)} claims with evidence from multiple sources",
        confidence=0.85
    )

    # Perform metacognitive analysis
    tracker.add_step(
        agent="Metacognitive_Analyzer",
        action="Assessing confidence and contradictions",
        reasoning="Analyzing evidence quality and detecting potential contradictions"
    )

    # Display metacognitive analysis for each claim
    if verbose and claim_results:
        print(f"\n{'='*70}")
        print("METACOGNITIVE ANALYSIS (Phase 2)")
        print(f"{'='*70}\n")

        # Analyze each claim with metacognitive layer
        escalations = []
        for i, claim_result in enumerate(claim_results, 1):
            claim_text = claim_result.claim
            verdict = claim_result.verdict
            confidence = claim_result.confidence
            evidence_list = claim_result.evidence_list
            metacog_detail = claim_result.metacognitive_detail

            print(f"\n{'='*70}")
            print(f"CLAIM {i}: {claim_text}")
            print(f"{'='*70}\n")

            # Step 0: Search Strategy (NEW - Educational Transparency)
            if metacog_detail and metacog_detail.search_queries:
                print("STEP 0: 🔍 SEARCH STRATEGY")
                print("-" * 50)
                print("The AI generated the following search queries:\n")

                for idx, query in enumerate(metacog_detail.search_queries, 1):
                    print(f"📌 Query {idx}: \"{query.query_text}\"")
                    print(f"   Tool: {query.source_tool}")
                    print(f"   Strategy: {query.search_strategy}")
                    print(f"   Reasoning: {query.query_reasoning}")
                    if query.results_count > 0:
                        print(f"   Results found: {query.results_count}")
                        if query.results_used > 0:
                            print(f"   Results assessed: {query.results_used}")
                    print()

                if metacog_detail.search_strategy_summary:
                    print(f"💡 SEARCH STRATEGY SUMMARY:")
                    print(f"   {metacog_detail.search_strategy_summary}\n")

                print()

            # Step 1: Evidence Analysis
            print("STEP 1: Evidence Gathered")
            print("-" * 50)
            if evidence_list:
                # Group evidence by type
                web_evidence = [e for e in evidence_list if e.source_type == "web_search"]
                wiki_evidence = [e for e in evidence_list if e.source_type == "wikipedia"]
                fact_check_evidence = [e for e in evidence_list if e.source_type == "fact_check"]

                print(f"Total Evidence Sources: {len(evidence_list)}")
                print(f"  - Web Search: {len(web_evidence)} sources")
                print(f"  - Wikipedia: {len(wiki_evidence)} sources")
                print(f"  - Fact-Check Databases: {len(fact_check_evidence)} sources\n")

                # Show evidence stance breakdown
                supporting = [e for e in evidence_list if e.stance == "supports"]
                refuting = [e for e in evidence_list if e.stance == "refutes"]
                neutral = [e for e in evidence_list if e.stance == "neutral"]
                unclear = [e for e in evidence_list if e.stance == "unclear"]

                print("Evidence Stance Breakdown:")
                print(f"  - Supporting: {len(supporting)} sources")
                print(f"  - Refuting: {len(refuting)} sources")
                print(f"  - Neutral: {len(neutral)} sources")
                print(f"  - Unclear: {len(unclear)} sources")

                # Calculate average credibility
                avg_credibility = sum(e.credibility_score for e in evidence_list) / len(evidence_list)
                print(f"\nAverage Source Credibility: {avg_credibility:.2f}")

                # Enhanced: Show detailed source-by-source assessment (if metacog_detail available)
                if metacog_detail and metacog_detail.sources_assessed:
                    print(f"\n" + "="*70)
                    print("DETAILED SOURCE-BY-SOURCE ASSESSMENT")
                    print("="*70 + "\n")

                    for src_idx, src_assess in enumerate(metacog_detail.sources_assessed, 1):
                        print(f"┌─────────────────────────────────────────────────────────────────┐")
                        print(f"│ SOURCE {src_idx}: {src_assess.source_name:<50} │")
                        print(f"│ Type: {src_assess.source_type:<58} │")
                        print(f"└─────────────────────────────────────────────────────────────────┘")
                        print()
                        print(f"🔗 URL: {src_assess.url}")
                        if src_assess.title:
                            print(f"📄 Title: {src_assess.title}")
                        print()

                        # CRAAP Assessment (for web sources)
                        if src_assess.craap_assessment and src_assess.source_type == "web_search":
                            craap = src_assess.craap_assessment
                            print(f"🎯 CRAAP TEST ASSESSMENT:")
                            print()
                            print(f"  C - Currency:  {craap.currency_score:.2f}/1.0")
                            print(f"      {craap.currency_notes}")
                            if craap.has_date:
                                print(f"      Has date: Yes")
                            print()

                            print(f"  R - Relevance: {craap.relevance_score:.2f}/1.0")
                            print(f"      {craap.relevance_notes}")
                            print(f"      Addresses claim: {craap.addresses_claim}")
                            print()

                            print(f"  A - Authority: {craap.authority_score:.2f}/1.0")
                            print(f"      {craap.authority_notes}")
                            print(f"      Domain type: {craap.domain_type}")
                            if craap.author_mentioned:
                                print(f"      Author credentials mentioned: Yes")
                            if craap.organization_clear:
                                print(f"      Organization clearly identified: Yes")
                            print()

                            print(f"  A - Accuracy:  {craap.accuracy_score:.2f}/1.0")
                            print(f"      {craap.accuracy_notes}")
                            print(f"      Tone: {craap.tone}")
                            if craap.cites_sources:
                                print(f"      Cites sources: Yes")
                            print()

                            print(f"  P - Purpose:   {craap.purpose_score:.2f}/1.0")
                            print(f"      {craap.purpose_notes}")
                            print(f"      Primary purpose: {craap.primary_purpose}")
                            if craap.bias_indicators:
                                print(f"      Bias indicators: {', '.join(craap.bias_indicators)}")
                            print()

                            print(f"  📊 Overall CRAAP Score: {craap.overall_craap_score:.2f}")
                            print(f"  ⭐ Final Credibility: {craap.credibility_score:.2f}/1.0")
                            print()

                        # Credibility (all sources)
                        print(f"⭐ Credibility: {src_assess.credibility_score:.2f}/1.0")
                        print(f"   {src_assess.credibility_reasoning}")
                        if src_assess.credibility_factors:
                            print(f"   Factors: {', '.join(src_assess.credibility_factors)}")
                        print()

                        # Relevance
                        print(f"📊 Relevance: {src_assess.relevance_score:.2f}/1.0")
                        print(f"   {src_assess.relevance_reasoning}")
                        if src_assess.relevance_factors:
                            print(f"   Factors: {', '.join(src_assess.relevance_factors)}")
                        print()

                        # Stance
                        stance_icon = {"supports": "✅", "refutes": "❌", "neutral": "⚖️", "unclear": "❓"}
                        print(f"📍 Stance: {src_assess.stance.upper()} {stance_icon.get(src_assess.stance, '')}")
                        print(f"   {src_assess.stance_reasoning}")
                        if src_assess.key_quotes:
                            print(f"\n   Key Evidence:")
                            for quote in src_assess.key_quotes:
                                print(f"   💬 \"{quote}\"")
                        print()

                        # Snippet
                        print(f"📄 Snippet:")
                        print(f"   {src_assess.snippet[:200]}...")
                        print()

                        if src_assess.publication_date:
                            print(f"🗓️  Publication Date: {src_assess.publication_date}")
                        if src_assess.author:
                            print(f"✍️  Author: {src_assess.author}")

                        print(f"\n{'-'*70}\n")
            else:
                print("No evidence found for this claim.")

            # Step 2: Contradiction Detection
            print(f"\n\nSTEP 2: Contradiction Analysis")
            print("-" * 50)
            contradiction = tracker.detect_contradictions(evidence_list)
            if contradiction.detected:
                print(f"⚠️  CONTRADICTIONS DETECTED")
                print(f"Severity: {contradiction.severity.upper()}")
                print(f"Description: {contradiction.description}")
                print(f"\nConflicting Sources:")
                for source in contradiction.contradicting_sources[:5]:  # Show up to 5
                    print(f"  - {source}")
            else:
                print("✓ No contradictions detected among sources")

            # Step 3: Sensitivity Analysis (LLM-based)
            print(f"\n\nSTEP 3: Sensitivity Detection (LLM Analysis)")
            print("-" * 50)
            # Call sensitivity analyzer
            sensitivity_result = await Runner.run(
                sensitivity_analyzer,
                claim_text
            )
            sensitivity_analysis: SensitivityAnalysis = sensitivity_result.final_output

            if sensitivity_analysis.is_sensitive:
                print(f"🔴 SENSITIVE TOPIC DETECTED")
                if sensitivity_analysis.sensitive_categories:
                    print(f"Categories: {', '.join(sensitivity_analysis.sensitive_categories)}")
                print(f"Reasoning: {sensitivity_analysis.reasoning}")
            else:
                print("✓ Not identified as sensitive topic")
                if sensitivity_analysis.reasoning:
                    print(f"Reasoning: {sensitivity_analysis.reasoning}")

            # Step 3.5: Verdict Decision Process (NEW - Educational Transparency)
            if metacog_detail and metacog_detail.verdict_reasoning:
                print(f"\n\nSTEP 3.5: 🤔 VERDICT DECISION PROCESS")
                print("-" * 50)
                vr = metacog_detail.verdict_reasoning

                print("The AI considered multiple verdict options. Here's the decision process:\n")

                # Evidence Weighting
                print("📊 EVIDENCE WEIGHTING CALCULATION:")
                print(f"   Supporting sources: {vr.supporting_sources_count} sources")
                print(f"   Supporting weight:  {vr.supporting_weight:.2f} (sum of credibility scores)")
                if vr.supporting_key_sources:
                    print(f"   Key sources: {', '.join(vr.supporting_key_sources[:3])}")
                print()

                print(f"   Refuting sources: {vr.refuting_sources_count} sources")
                print(f"   Refuting weight:  {vr.refuting_weight:.2f} (sum of credibility scores)")
                if vr.refuting_key_sources:
                    print(f"   Key sources: {', '.join(vr.refuting_key_sources[:3])}")
                print()

                print(f"   Neutral sources: {vr.neutral_sources_count} sources")
                print(f"   Neutral weight:  {vr.neutral_weight:.2f}")
                print()

                # Evidence weight visualization
                total_weight = vr.supporting_weight + vr.refuting_weight + vr.neutral_weight
                if total_weight > 0:
                    print("   EVIDENCE WEIGHT VISUALIZATION:")
                    supp_bars = int((vr.supporting_weight / max(total_weight, 1)) * 40)
                    ref_bars = int((vr.refuting_weight / max(total_weight, 1)) * 40)
                    neut_bars = int((vr.neutral_weight / max(total_weight, 1)) * 40)
                    print(f"   Supporting  [{'█' * supp_bars:<40}] {vr.supporting_weight:.2f}")
                    print(f"   Refuting    [{'█' * ref_bars:<40}] {vr.refuting_weight:.2f}")
                    print(f"   Neutral     [{'█' * neut_bars:<40}] {vr.neutral_weight:.2f}")
                    print()

                # Verdict alternatives considered
                print("🔍 VERDICT ALTERNATIVES CONSIDERED:")
                print()

                all_verdicts = ["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
                for alt_verdict in all_verdicts:
                    if alt_verdict == vr.final_verdict:
                        print(f"   ✅ {alt_verdict} - SELECTED")
                    else:
                        print(f"   ❌ {alt_verdict} - Rejected")

                if vr.why_not_alternatives:
                    print(f"\n   Why alternatives were rejected:")
                    print(f"   {vr.why_not_alternatives}")
                print()

                # Primary reason
                print("🎯 PRIMARY REASON FOR VERDICT:")
                print(f"   {vr.primary_reason}")
                print()

                # Decisive factor
                if vr.decisive_factor:
                    print("⚡ DECISIVE FACTOR:")
                    print(f"   {vr.decisive_factor}")
                    print()

                if vr.decisive_sources:
                    print("   Decisive sources:")
                    for ds in vr.decisive_sources:
                        print(f"   • {ds}")
                    print()

                # Decision rule applied
                if vr.decision_rule_applied:
                    print(f"📋 DECISION RULE APPLIED:")
                    print(f"   {vr.decision_rule_applied}")
                    print()

                # Confidence reasoning
                print(f"🎚️  CONFIDENCE: {vr.confidence:.2f}")
                if vr.confidence_reasoning:
                    print(f"   Reasoning: {vr.confidence_reasoning}")
                if vr.confidence_factors:
                    print(f"   Factors:")
                    for factor in vr.confidence_factors:
                        print(f"   • {factor}")
                print()

            # Step 4: Confidence Assessment
            print(f"\n\nSTEP 4: Confidence Assessment")
            print("-" * 50)
            print(f"Final Confidence: {confidence:.2f}")
            print(f"\nConfidence Factors:")
            if evidence_list:
                supporting_weight = sum(e.credibility_score for e in supporting)
                refuting_weight = sum(e.credibility_score for e in refuting)
                print(f"  - Supporting Evidence Weight: {supporting_weight:.2f}")
                print(f"  - Refuting Evidence Weight: {refuting_weight:.2f}")
                print(f"  - Number of Sources: {len(evidence_list)}")
                print(f"  - Average Credibility: {avg_credibility:.2f}")

            # Step 5: Escalation Decision
            print(f"\n\nSTEP 5: Escalation Decision")
            print("-" * 50)
            escalation = escalation_mgr.should_escalate(
                claim=claim_text,
                verdict=verdict,
                confidence=confidence,
                contradiction=contradiction,
                evidence_list=evidence_list,
                sensitivity_analysis=sensitivity_analysis
            )

            if escalation.should_escalate:
                print("🚨 ESCALATION TO INSTRUCTOR REQUIRED")
                print("\nReasons:")
                for reason in escalation.reasons:
                    print(f"  - {reason}")
                escalations.append((i, claim_text, escalation))
            else:
                print("✓ No escalation needed - sufficient confidence and clarity")

            # Step 6: AI Limitations & Uncertainties (NEW - Educational Transparency)
            if metacog_detail:
                print(f"\n\nSTEP 6: 🔬 AI LIMITATIONS & UNCERTAINTIES")
                print("-" * 50)
                print("The AI wants students to understand where this assessment may be limited:\n")

                # What the AI couldn't determine
                if metacog_detail.ai_uncertainties:
                    print("❓ WHAT THE AI COULDN'T DETERMINE:")
                    for idx, uncertainty in enumerate(metacog_detail.ai_uncertainties, 1):
                        print(f"   {idx}. {uncertainty}")
                    print()

                # Assumptions made
                if metacog_detail.assumptions_made:
                    print("🤔 ASSUMPTIONS MADE:")
                    for idx, assumption in enumerate(metacog_detail.assumptions_made, 1):
                        print(f"   {idx}. {assumption}")
                    print()

                # Potential weaknesses
                if metacog_detail.potential_weaknesses:
                    print("⚠️  POTENTIAL WEAKNESSES IN THIS ASSESSMENT:")
                    for idx, weakness in enumerate(metacog_detail.potential_weaknesses, 1):
                        print(f"   {idx}. {weakness}")
                    print()

                # Metacognitive summary
                if metacog_detail.metacognitive_summary:
                    print("💡 METACOGNITIVE SUMMARY FOR STUDENTS:")
                    print(f"   {metacog_detail.metacognitive_summary}")
                    print()

                # Assessment time (if tracked)
                if metacog_detail.total_assessment_time:
                    print(f"⏱️  Total Assessment Time: {metacog_detail.total_assessment_time:.1f} seconds")
                    print()

            # Final Verdict Summary
            print(f"\n\nFINAL VERDICT SUMMARY")
            print("-" * 50)
            print(f"Verdict: {verdict}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Justification: {claim_result.justification[:200]}...")
            print()

        # Display reasoning path
        print(f"\n{'='*70}")
        print("REASONING PATH")
        print(f"{'='*70}")
        print(f"{tracker.get_reasoning_path()}")

        # Display escalation details
        if escalations:
            print(f"\n{'='*70}")
            print("ESCALATION DETAILS")
            print(f"{'='*70}\n")

            for claim_num, claim_text, escalation in escalations:
                print(f"Claim {claim_num}: {claim_text}\n")
                print(f"Reasons:")
                for reason in escalation.reasons:
                    print(f"  - {reason}")
                print(f"\nSuggested Actions:")
                for action in escalation.suggested_actions:
                    print(f"  - {action}")
                print(f"\n{escalation.instructor_notes}\n")

    # Calculate overall confidence from structured results
    overall_confidence = sum(cr.confidence for cr in claim_results) / len(claim_results) if claim_results else 0.5

    # Create final assessment with structured results
    assessment = FinalAssessment(
        input_text=text,
        total_claims=len(claim_results),
        claim_results=claim_results,  # Use the structured VerificationResults
        overall_credibility=f"Average Confidence: {overall_confidence:.2f}"
    )

    return assessment


async def main():
    """Test the enhanced MetaCheck system"""

    # Test text with multiple testable claims
    test_text = """
    Donald Trump increased military recruitment in 2025.
    """

    result = await verify_claims(test_text, verbose=True)

    print(f"\n{'='*70}")
    print("ASSESSMENT COMPLETE")
    print(f"{'='*70}")
    print(f"Total claims processed: {result.total_claims}")
    print(f"Generated at: {result.generated_at}")


if __name__ == "__main__":
    asyncio.run(main())
