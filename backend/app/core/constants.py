"""
MetaCheck Constants

Verdict criteria, metacognitive instructions, and model configuration.
"""

from app.core.settings import get_settings
from app.core.tool_settings import load_tool_settings

# Load settings and model name
settings = get_settings()
MODEL_NAME = settings.open_ai_model  # Default: gpt-4.1 (configured in settings.py)
tool_settings = load_tool_settings()

# ============================================================================
# TEXT AND CLAIM LIMITS
# ============================================================================

# Maximum text length for verification (characters)
MAX_TEXT_LENGTH = 2000

# Maximum number of claims that can be verified per mode
MAX_CLAIMS_BASIC = int(
    tool_settings["verification_scope"]["basic"]["max_claims_to_verify_per_run"]
)
MAX_CLAIMS_COMPREHENSIVE = int(
    tool_settings["verification_scope"]["comprehensive"]["max_claims_to_verify_per_run"]
)

# Maximum number of claims shown for extraction-oriented settings UI
MAX_CLAIMS_EXTRACT = int(
    max(
        tool_settings["verification_scope"]["basic"]["max_claims_to_extract"],
        tool_settings["verification_scope"]["comprehensive"]["max_claims_to_extract"],
    )
)

# Per-claim timeout in seconds for claim verification orchestration
PER_CLAIM_TIMEOUT_SECONDS = float(
    tool_settings["performance_cost_controls"]["per_claim_timeout_seconds"]
)


# ============================================================================
# VERDICT CRITERIA
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


# ============================================================================
# METACOGNITIVE INSTRUCTIONS
# ============================================================================

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
# EXTRACTION INSTRUCTIONS
# ============================================================================

EXTRACTION_INSTRUCTIONS = """
You are an expert claim extraction agent trained in professional fact-checking workflows (e.g., PolitiFact, Snopes, Full Fact, FactCheck.org).

Your task is to extract ONLY claims that:

* are specific, checkable, and falsifiable
* require consulting external sources to verify
* assert something about reality that could be proven TRUE or FALSE
* contain concrete details (e.g., numbers, dates, causes, names, locations, comparisons, predictions)

DO NOT extract:

* well-known or widely accepted facts (e.g., "The Earth orbits the sun")
* general knowledge or definitions
* opinions or value judgments
* vague statements without verifiable details
* personal feelings or beliefs
* generic background information
* statements that are true by definition
* promotional or descriptive text without factual assertions

Extract a claim ONLY if it satisfies ALL of the following:

1. Falsifiable (can be proven wrong)
2. Specific (not generic)
3. Contextualized (linked to an entity, time, place, or number)
4. Requires external verification

IMPORTANT - Split compound claims:

If a sentence contains multiple independent facts joined by "and", "while", "also", etc., extract EACH fact as a separate claim. Independent facts require different evidence sources and one could be true while another is false.

Example input: "The Eiffel Tower is 330 meters tall and attracts 7 million visitors annually."
Correct extraction:
  - "The Eiffel Tower is 330 meters tall."
  - "The Eiffel Tower attracts 7 million visitors annually."

Example input: "Tesla sold 1.8 million cars in 2023 and became the most valuable automaker."
Correct extraction:
  - "Tesla sold 1.8 million cars in 2023."
  - "Tesla became the most valuable automaker."

Do NOT split when facts are logically dependent (cause-effect, condition-result):
  - "The vaccine reduced infections by 90% in clinical trials." (single claim - result tied to context)

Before extracting a claim, ask yourself:

"Would a fact-checking organization realistically publish a fact-check article about this statement?"

If the answer is NO -> do NOT extract it.


---

INCLUDE examples:

* "Finland generates 40% of its electricity from nuclear power."
* "The company increased its revenue by 25% in 2024."
* "Apple will release a new AI chip in March 2025."
* "WHO declared COVID-19 a pandemic on March 11, 2020."

EXCLUDE examples:

* "The sky is blue."
* "Finland is a Nordic country."
* "AI is becoming more popular."
* "This product is innovative."
* "Climate change is real."
* "The company is a market leader."

---

OUTPUT FORMAT (JSON list):

[
  {"text": "..."},
  {"text": "..."}
]

If no verifiable claims exist, return:

[]
"""
