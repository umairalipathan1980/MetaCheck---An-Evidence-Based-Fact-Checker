"""
MetaCheck - Metacognitive Information-Assessment Tool
"""

import asyncio
import os
import json
from datetime import datetime
from typing import List, Optional, Literal, Dict
from urllib.parse import urlparse
from pydantic import BaseModel, Field
import requests

from agents import Agent, WebSearchTool, Runner, ModelSettings, function_tool
from app.core.settings import get_settings

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

settings = get_settings()
MODEL_NAME = settings.open_ai_model  # Default: gpt-4.1 (configured in settings.py)


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

INSUFFICIENT_INFORMATION - Use when:
- Very limited evidence (fewer than 2 sources total)
- ALL available sources lack credibility (<0.7)
- Evidence is indirect, vague, or incomplete on ALL sides
- Key information missing for verification
- Evidence is outdated for time-sensitive claims
- IMPORTANT: Do NOT use INSUFFICIENT_INFORMATION when credible evidence (>=0.7) clearly refutes or supports the claim, even if some low-credibility sources disagree

CONFLICTING_EVIDENCE - Use when:
- Multiple CREDIBLE sources (>=0.7) present opposing views on BOTH sides
- Both supporting and refuting sides have credible evidence
- No clear resolution from available evidence
- Credibility and quantity roughly balanced between both sides
- IMPORTANT: Requires genuine conflict between credible sources, not low-credibility vs credible sources

Evidence Weighting Rules:
1. Credibility score thresholds:
   - High-credibility sources: > 0.8 (e.g., fact-checkers at 0.95)
   - Credible sources: >= 0.7 (e.g., Wikipedia at 0.8, web sources 0.70-0.85 from domain classification)
   - Low-credibility sources: < 0.7 (e.g., general web 0.60, user-generated 0.50 from domain classification)

2. Weight evidence by credibility score:
   - High-credibility sources (>0.8) have strongest weight
   - Credible sources (>=0.7) should dominate verdict over low-credibility sources
   - Compare total credibility weight: sum of credibility scores on each side

3. Decision priority:
   - If credible sources (>=0.7) clearly support or refute, use SUPPORTED/REFUTED
   - If credible sources conflict, use CONFLICTING_EVIDENCE
   - Only use INSUFFICIENT_INFORMATION when no credible sources exist or all are unclear
   - Example: 1 high-cred refuting (0.95) outweighs multiple low-cred supporting (0.6, 0.5)

Decision rule: Weight evidence by credibility. Credible sources (>=0.7) dominate verdict decisions.
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
      - Classify the domain using domain-based credibility assessment
      - Document which domain category was identified (government, academic, news, etc.)
      - Explain the credibility score based on domain type
      - Note limitations: "Assessment based on domain reputation only, not content quality"

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
      - List each possible verdict (SUPPORTED, REFUTED, INSUFFICIENT_INFORMATION, CONFLICTING_EVIDENCE)
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
    - CONFLICTING_EVIDENCE: Rejected (requires credible sources on BOTH sides, we only have refuting)
    - INSUFFICIENT_INFORMATION: Rejected (we have 4 high-credibility sources, not insufficient)

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
    verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT_INFORMATION", "CONFLICTING_EVIDENCE"]
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
    mode: Literal["basic", "comprehensive"] = "basic"
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


class SearchQuery(BaseModel):
    """Record of search queries generated by the AI for educational transparency"""
    query_text: str
    query_reasoning: str  # WHY this query was generated
    search_strategy: Literal["direct", "broad", "contextual", "fact_check"]
    source_tool: Literal["WebSearchTool", "wikipedia_search_tool", "google_fact_check_tool"]
    timestamp: datetime = Field(default_factory=datetime.now)
    results_count: int = 0
    results_used: int = 0  # How many results were actually assessed


class DomainClassification(BaseModel):
    """Domain-based credibility classification result"""
    credibility_score: float = Field(ge=0.0, le=1.0)
    category: str  # e.g., "government_public", "scientific_journals", "general_web"
    description: str
    reasoning: str
    justification: str
    limitations: str


class SourceAssessment(BaseModel):
    """Detailed assessment of a single source for educational transparency"""
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    title: str = ""

    # Domain classification (only for web_search)
    domain_category: Optional[str] = None  # e.g., "government_public", "scientific_journals"
    domain_classification: Optional[DomainClassification] = None  # Full classification result from classify_web_source()

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
    final_verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT_INFORMATION", "CONFLICTING_EVIDENCE"]
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
    alternative_verdicts_considered: List[str] = []  # e.g., ["CONFLICTING_EVIDENCE", "INSUFFICIENT_INFORMATION"]
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

        elif verdict == "CONFLICTING_EVIDENCE":
            # Conflicting evidence means lower confidence
            base_confidence = 0.4

        elif verdict == "INSUFFICIENT_INFORMATION":
            base_confidence = 0.3

        else:
            base_confidence = 0.2

        # Adjust based on evidence credibility
        avg_credibility = sum(e.credibility_score for e in evidence_list) / len(evidence_list)
        confidence = (base_confidence + avg_credibility) / 2

        return min(1.0, max(0.0, confidence))

    def detect_contradictions(self, evidence_list: List[Evidence]) -> ContradictionDetection:
        """
        Detect contradictory evidence and assess severity.

        Uses tiered credibility thresholds:
        - Credible sources: >= 0.7 (fact-checkers 0.95, Wikipedia 0.8, web_search 0.50-0.85 from domain classification)
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
        - Sensitive topic identified by LLM analysis
        """
        reasons: List[str] = []
        should_escalate = False

        if confidence < self.CONFIDENCE_THRESHOLD:
            if contradiction.detected:
                should_escalate = True
                reasons.append(f"Low confidence ({confidence:.2f}) combined with contradictory evidence")
            if sensitivity_analysis and sensitivity_analysis.is_sensitive:
                should_escalate = True
                categories_str = ", ".join(sensitivity_analysis.sensitive_categories) if sensitivity_analysis.sensitive_categories else "general"
                reasons.append(f"Low confidence ({confidence:.2f}) on sensitive topic ({categories_str})")

        if contradiction.detected and contradiction.severity == "major":
            should_escalate = True
            reasons.append("Major contradictions detected between credible sources")

        if verdict == "INSUFFICIENT_INFORMATION" and len(evidence_list) < 2:
            if sensitivity_analysis and sensitivity_analysis.is_sensitive:
                should_escalate = True
                reasons.append("Insufficient evidence for sensitive claim")

        instructor_notes = self._generate_instructor_notes(
            claim, verdict, confidence, contradiction, evidence_list, reasons
        )
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
            notes += "Contradiction Analysis:\n"
            notes += f"  Severity: {contradiction.severity.upper()}\n"
            notes += f"  {contradiction.description}\n"
            notes += "  Contradicting sources:\n"
            for source in contradiction.contradicting_sources:
                notes += f"    - {source}\n"
            notes += "\n"

        notes += "Evidence Summary:\n"
        notes += f"  Total sources: {len(evidence_list)}\n"

        by_type: Dict[str, int] = {}
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
        actions: List[str] = []

        if contradiction.detected:
            actions.append("Review contradictory sources directly for nuance")
            actions.append("Consult domain experts if needed")

        if verdict == "INSUFFICIENT_INFORMATION":
            actions.append("Conduct additional manual research")
            actions.append("Consider specialized databases or academic sources")

        if verdict == "CONFLICTING_EVIDENCE":
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


# extraction_instructions = """ You are a claim extractor who has expertise in extracting verifiable claims from contents. 
# Use a moderate approach to extract only those claims which warrant exploring different fact checking sources for verification. 
# Do not extract well-known facts as claims. Return a list of extracted claims in structured format. """


extraction_instructions = """
You are an expert claim extraction agent trained in professional fact-checking workflows (e.g., PolitiFact, Snopes, Full Fact, FactCheck.org).

Your task is to extract ONLY claims that:

• are specific, checkable, and falsifiable
• require consulting external sources to verify
• assert something about reality that could be proven TRUE or FALSE
• contain concrete details (e.g., numbers, dates, causes, names, locations, comparisons, predictions)

DO NOT extract:

• well-known or widely accepted facts (e.g., "The Earth orbits the sun")
• general knowledge or definitions
• opinions or value judgments
• vague statements without verifiable details
• personal feelings or beliefs
• generic background information
• statements that are true by definition
• promotional or descriptive text without factual assertions

Extract a claim ONLY if it satisfies ALL of the following:

1. Falsifiable (can be proven wrong)
2. Specific (not generic)
3. Contextualized (linked to an entity, time, place, or number)
4. Requires external verification

Before extracting a claim, ask yourself:

"Would a fact-checking organization realistically publish a fact-check article about this statement?"

If the answer is NO → do NOT extract it.


---

✅ INCLUDE examples:

• "Finland generates 40% of its electricity from nuclear power."
• "The company increased its revenue by 25% in 2024."
• "Apple will release a new AI chip in March 2025."
• "WHO declared COVID-19 a pandemic on March 11, 2020."

❌ EXCLUDE examples:

• "The sky is blue."
• "Finland is a Nordic country."
• "AI is becoming more popular."
• "This product is innovative."
• "Climate change is real."
• "The company is a market leader."

---

OUTPUT FORMAT (JSON list):

[
  {"text": "..."},
  {"text": "..."}
]

If no verifiable claims exist, return:

[]
"""

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# External API clients (used as tools)
google_fact_check_client = GoogleFactCheckClient()
wikipedia_client = WikipediaClient()


# ============================================================================
# DOMAIN CLASSIFICATION (Replaces CRAAP Agent)
# ============================================================================

def load_domain_config() -> Dict:
    """Load domain classification config from config.json"""
    # Look for explicit override, then file-local, then CWD
    candidates = []
    env_path = os.getenv("METACHECK_CONFIG_PATH")
    if env_path:
        candidates.append(env_path)

    # Path relative to this file
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(base_dir, "config.json"))
    except Exception:
        pass

    # Fallback to working directory
    candidates.append("config.json")

    for path in candidates:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except Exception as exc:
            print(f"Warning: failed to load config from {path}: {exc}")

    print("Warning: config.json not found, using defaults")
    return {"default_score": 0.6, "categories": {}, "resolution_order": []}

def classify_web_source(url: str, title: str = "", snippet: str = "") -> Dict:
    """
    Fast domain-based credibility assessment using config.json.

    Args:
        url: Source URL
        title: Article title (optional, for context)
        snippet: Article snippet (optional, for context)

    Returns:
        {
            'credibility_score': float (0.50-0.85),
            'category': str,
            'description': str,
            'reasoning': str,
            'justification': str,
            'limitations': str
        }
    """
    config = load_domain_config()

    # Parse URL
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
    except Exception:
        # Invalid URL, return default
        return {
            'credibility_score': config.get('default_score', 0.6),
            'category': 'general_web',
            'description': 'General web source (invalid URL)',
            'reasoning': 'Could not parse URL; using default credibility',
            'justification': 'Standard web content with variable editorial oversight',
            'limitations': 'Quality and accuracy varies widely; no systematic fact-checking'
        }

    # Check categories in resolution order
    categories = config.get('categories', {})
    resolution_order = config.get('resolution_order', [])

    for category_key in resolution_order:
        if category_key not in categories:
            continue

        category = categories[category_key]

        # Check domain whitelist (exact match)
        if domain in category.get('domain_whitelist', []):
            return {
                'credibility_score': category['score'],
                'category': category_key,
                'description': category['description'],
                'reasoning': f"Domain '{domain}' identified as {category['description']}",
                'justification': category.get('justification', 'Source matches known credible domain'),
                'limitations': category.get('limitations', 'Assessment based on domain reputation only')
            }

        # Check subdomain suffixes (e.g., .github.io, .wordpress.com)
        subdomain_suffixes = category.get('subdomain_suffixes', [])
        for suffix in subdomain_suffixes:
            if domain.endswith(suffix):
                return {
                    'credibility_score': category['score'],
                    'category': category_key,
                    'description': category['description'],
                    'reasoning': f"Domain '{domain}' matches pattern '{suffix}' for {category['description']}",
                    'justification': category.get('justification', 'Source matches known pattern'),
                    'limitations': category.get('limitations', 'Assessment based on domain pattern only')
                }

        # Check TLD patterns (e.g., .gov, .edu, .ac.uk)
        tld_patterns = category.get('tld_patterns', [])
        for tld in tld_patterns:
            if domain.endswith(tld):
                return {
                    'credibility_score': category['score'],
                    'category': category_key,
                    'description': category['description'],
                    'reasoning': f"Domain '{domain}' has TLD '{tld}' indicating {category['description']}",
                    'justification': category.get('justification', 'TLD indicates institutional source'),
                    'limitations': category.get('limitations', 'Assessment based on domain type only')
                }

    # No match found, use default
    default_score = config.get('default_score', 0.6)
    general_cat = categories.get('general_web', {})

    return {
        'credibility_score': default_score,
        'category': 'general_web',
        'description': general_cat.get('description', 'General web source'),
        'reasoning': f"Domain '{domain}' not recognized; using default credibility assessment",
        'justification': general_cat.get('justification', 'Standard web content with variable editorial oversight'),
        'limitations': general_cat.get('limitations', 'Quality varies widely; no systematic fact-checking; author credentials unknown')
    }


# Domain classification tool for orchestrator
@function_tool
def domain_classification_tool(url: str) -> DomainClassification:
    """
    Classify a web domain's credibility using config.json.

    Args:
        url: The web source URL to classify

    Returns:
        DomainClassification with credibility score and reasoning
    """
    result = classify_web_source(url)
    return DomainClassification(**result)


# ============================================================================
# AGENTS
# ============================================================================

# 1. Claim Extractor Agent
claim_extractor = Agent(
    name="claim_extractor",
    instructions=extraction_instructions,
    model=MODEL_NAME,
    output_type=ClaimList,
)


# 1b. Sensitivity Analyzer Agent
sensitivity_analyzer = Agent(
    name="sensitivity_analyzer",
    model=MODEL_NAME,
    model_settings=ModelSettings(
        max_completion_tokens=4096,
        temperature=0.1
    ),
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

# 5. Metacognitive Orchestrator (with direct access to all tools)
orchestrator = Agent(
    name="metacognitive_orchestrator",
    model=MODEL_NAME,
    model_settings=ModelSettings(
        max_completion_tokens=16384,  # Increased from default ~4096 to handle multiple claims
        temperature=0.1  # Lower temperature for more consistent, deterministic factual outputs
    ),
    instructions=f"""You are the MetaCheck orchestrator coordinating a fact-checking workflow.

Your task:
1. Use 'claim_extractor' to extract check-worthy claims from input text
2. For EACH claim extracted:
   a. Use 'WebSearchTool' to search the web for evidence
   b. For EACH web_search result, classify domain credibility (see workflow below)
   c. Use 'wikipedia_search_tool' to search Wikipedia for evidence
   d. Use 'google_fact_check_tool' to query professional fact-checking databases
   e. Synthesize ALL evidence and apply VERDICT_CRITERIA to reach a structured verdict

{VERDICT_CRITERIA}

{METACOGNITIVE_INSTRUCTIONS}

For each claim, you MUST create a VerificationResult with:
- claim: The exact claim text (string)
- verdict: MUST be one of [SUPPORTED, REFUTED, INSUFFICIENT_INFORMATION, CONFLICTING_EVIDENCE]
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
      - web_search: Domain-based credibility (range 0.50-0.85, see domain classification below)
    * stance: "supports", "refutes", "neutral", or "unclear"

  WORKFLOW for web_search sources (domain-based classification):
  1. Get web search results from WebSearchTool
  2. For EACH result, call domain_classification_tool with the URL
     - This tool returns DomainClassification with:
       * credibility_score (0.50-0.85 range)
       * category (e.g., "government_public", "scientific_journals", "general_web")
       * description, reasoning, justification, limitations
  3. Create Evidence object using credibility_score from domain_classification_tool
  4. Store the full DomainClassification result for educational transparency

  Example domain classifications:
  - government/intergovernmental (.gov, who.int, un.org) → 0.85
  - scientific journals (nature.com, science.org, nejm.org) → 0.82
  - academic (.edu, .ac.uk, ieee.org) → 0.80
  - medical institutions (cdc.gov, mayoclinic.org) → 0.75
  - established news (nytimes.com, bbc.com, reuters.com) → 0.75
  - think tanks (brookings.edu, rand.org) → 0.72
  - international news (aljazeera.com, dw.com) → 0.70
  - general web (unknown domains) → 0.60
  - user-generated (medium.com, reddit.com) → 0.50
  - low-trust (bit.ly, tinyurl.com) → 0.50

  Example for web_search: Evidence(source_name="CDC", source_type="web_search", url="https://www.cdc.gov/...", snippet="Vaccines are safe...", relevance_score=0.9, credibility_score=0.75, stance="supports")
  Example for wikipedia: Evidence(source_name="Wikipedia: COVID-19", source_type="wikipedia", url="https://en.wikipedia.org/...", snippet="COVID-19 is...", relevance_score=0.95, credibility_score=0.8, stance="supports")
  Example for fact_check: Evidence(source_name="Snopes", source_type="fact_check", url="https://www.snopes.com/...", snippet="Claim is false...", relevance_score=1.0, credibility_score=0.95, stance="refutes")
- metacognitive_steps: Can be empty list []

Metacognitive awareness:
- Track confidence for each step
- Note when evidence is contradictory
- Recommend careful review for low-confidence (<0.6) or sensitive claims
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
        domain_classification_tool,
        wikipedia_search_tool,
        google_fact_check_tool,
    ],
    output_type=OrchestratorOutput,
)


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

async def verify_claims(
    text: str,
    verbose: bool = True,
    mode: Literal["basic", "comprehensive"] = "basic",
) -> FinalAssessment:
    """
    Main MetaCheck workflow with Phase 2 metacognitive layer.

    Args:
        text: Input text to analyze
        verbose: Print progress information
        mode: "basic" for concise outputs (default) or "comprehensive" for full metacognitive detail

    Returns:
        FinalAssessment with all results and metacognitive analysis
    """
    selected_mode = mode.lower()
    if selected_mode not in {"basic", "comprehensive"}:
        raise ValueError(f"Invalid mode '{mode}'. Expected 'basic' or 'comprehensive'.")

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

    # Run orchestrator to coordinate entire workflow (model settings configured in Agent)
    tracker.add_step(
        agent="Orchestrator",
        action="Coordinating multi-agent fact-checking",
        reasoning="Extracting claims and gathering evidence from multiple sources"
    )

    result = await Runner.run(
        orchestrator,
        (
            f"MODE: {selected_mode.upper()}.\n"
            "If mode=BASIC: return only claim, verdict, confidence, a 1-2 sentence justification, "
            "key_sources (name + URL), and evidence_list with source_name/source_type/url/stance/credibility_score/"
            "relevance_score. Set metacognitive_steps as [] and metacognitive_detail as null. Skip verbose or "
            "step-by-step metacognitive narration.\n"
            "If mode=COMPREHENSIVE: include the full metacognitive detail and transparency required in the system "
            "instructions.\n\n"
            f"Analyze this text and fact-check all claims: {text}"
        ),
        max_turns=30  # Allow enough turns for multiple claims with multiple tool calls each
    )

    # Get structured output from orchestrator
    orchestrator_output: OrchestratorOutput = result.final_output
    claim_results = orchestrator_output.claim_results

    # Trim results for basic mode to avoid returning extra reasoning fields
    if selected_mode == "basic":
        for cr in claim_results:
            cr.metacognitive_steps = []
            cr.metacognitive_detail = None

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
    if verbose and claim_results and selected_mode == "comprehensive":
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

                        # Domain Classification (for web sources)
                        if src_assess.domain_classification and src_assess.source_type == "web_search":
                            domain_info = src_assess.domain_classification
                            print(f"🏷️  DOMAIN CLASSIFICATION:")
                            print()
                            print(f"  Category: {domain_info.category}")
                            print(f"  Description: {domain_info.description}")
                            print(f"  Credibility Score: {domain_info.credibility_score:.2f}/1.0")
                            print()
                            print(f"  📝 Reasoning:")
                            print(f"     {domain_info.reasoning}")
                            print()
                            print(f"  ✓ Justification:")
                            print(f"     {domain_info.justification}")
                            print()
                            print(f"  ⚠️  Limitations:")
                            print(f"     {domain_info.limitations}")
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

                all_verdicts = ["SUPPORTED", "REFUTED", "INSUFFICIENT_INFORMATION", "CONFLICTING_EVIDENCE"]
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
        overall_credibility=f"Average Confidence: {overall_confidence:.2f}",
        mode=selected_mode,
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