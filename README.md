# MetaCheck: Metacognitive Information Assessment System

A multi-agent fact-checking system with metacognitive awareness, self-monitoring capabilities, and reasoning visibility designed for teaching AI literacy and critical thinking.

---

## Overview

MetaCheck is a three-phase fact-checking and **educational system** that combines:
1. **Multi-agent orchestration** for comprehensive evidence gathering
2. **Metacognitive self-monitoring** for reasoning transparency and quality control
3. **Full educational transparency** showing students HOW AI evaluates information (NEW in v3.0)

The system analyzes text, extracts factual claims, gathers evidence from multiple sources, and provides verdicts with confidence assessments and **complete reasoning traces for educational purposes**.

### Features

- **Educational-First Design**: Every reasoning step documented for teaching AI literacy
- **Complete Transparency**: Shows search queries, source assessments, decision logic, and limitations
- **CRAAP Test Integration**: Systematic source evaluation framework visible to students
- **Structured Output**: Uses Pydantic models to ensure predictable, type-safe results
- **Dynamic Claim Handling**: Automatically handles any number of claims (not hard-coded)
- **Multi-Source Evidence**: Combines web search, Wikipedia, and professional fact-checkers
- **Self-Aware**: Tracks confidence, detects contradictions, and flags when expert review is needed
- **Verdict Reasoning**: Shows alternatives considered and why they were rejected
- **Acknowledges Limitations**: Explicitly states what the AI couldn't determine or might be wrong about

---

## Educational Purpose

MetaCheck is designed as a **teaching tool** for AI literacy and critical thinking in higher education:

### Target Audience
- **Students**: Learn how AI evaluates information, detects misinformation, and makes decisions
- **Educators**: Use as a teaching aid for media literacy, information evaluation, and AI literacy courses
- **Researchers**: Study AI decision-making transparency and metacognitive systems

### Learning Objectives

Students using MetaCheck will:
1. **Understand Source Evaluation**: See how the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose) is applied systematically
2. **Learn Evidence Weighting**: Understand how credibility scores determine verdicts
3. **Recognize AI Limitations**: See where AI makes assumptions and might be wrong
4. **Develop Critical Thinking**: Compare their own assessments with AI's reasoning
5. **Understand Decision Logic**: See why certain verdicts were chosen over alternatives

### Educational Transparency Features 

MetaCheck shows students **every step of the AI's reasoning**:

#### Step 0: Search Strategy
- What queries the AI generated and why
- What search strategy was used (direct, broad, contextual, fact-check)
- How many results were found and assessed

#### Step 1: Source-by-Source Assessment
- Complete CRAAP test breakdown for web sources
- Credibility scoring with transparent reasoning
- Stance determination with key quotes from sources
- Relevance assessment with specific factors

#### Step 3.5: Verdict Decision Process
- Evidence weighting calculation (sum of credibility scores)
- Visual representation of supporting vs. refuting evidence
- All verdict alternatives considered (SUPPORTED, REFUTED, INSUFFICIENT, CONFLICTING, NEEDS_INSTRUCTOR)
- Explanation of why each alternative was selected or rejected
- Decisive factors and decisive sources identified

#### Step 6: AI Limitations & Uncertainties
- What the AI couldn't determine (e.g., "couldn't access full articles")
- What assumptions were made (e.g., "assumed fact-checkers have 0.95 credibility")
- Potential weaknesses in the assessment
- Metacognitive summary for students

### Pedagogical Design Principles

1. **Show Your Work**: Never hide reasoning - transparency over polish
2. **Acknowledge Uncertainty**: Be honest about limitations and gaps
3. **Invite Comparison**: Students can contrast their thinking with AI's process
4. **Progressive Disclosure**: Information organized in clear steps
5. **Encourage Skepticism**: Explicitly note where AI might be wrong

---

## Architecture

```
User Input Text
       ↓
verify_claims() [Main Entry Point]
       ↓
Metacognitive Orchestrator (with METACOGNITIVE_INSTRUCTIONS)
       ↓
   ┌───┴─────────────────────────────────────────────────────────┐
   │                              │                               │
   ▼                              ▼                               ▼
Phase 1:                    Phase 2:                       Phase 3:
Multi-Agent              Metacognitive                 Educational
Fact-Checking               Analysis                   Transparency (NEW)
       ↓                              ↓                               ↓
   ┌───┴───────────┐           ┌──────┴─────────┐          ┌─────────┴──────────┐
   │               │           │                │          │                    │
   ▼               ▼           ▼                ▼          ▼                    ▼
Claim          Evidence    Confidence      Escalation   Search           Verdict
Extraction     Gathering   Assessment      Management   Strategy       Reasoning
   │               │           │                │          │                    │
   │        ┌──────┼──────┐    │                │          │                    │
   │        ▼      ▼      ▼    │                │          ▼                    ▼
   │     Web   Wiki  Fact-     │                │     Query            Source-by-Source
   │    Search       Check      │                │   Generation          Assessment
   │        │      │      │     │                │       +                   +
   │        │      │      │     │                │   Strategy           CRAAP Test
   │        ▼      ▼      ▼     │                │                           │
   │   CRAAP Source Source      │                │                           ▼
   │   Assess Assess Assess     │                │                    Evidence
   │        │      │      │     │                │                    Weighting
   └────────┴──────┴──────┴─────┴────────────────┴────────────────────────────┘
                                      ↓
                          Structured Results with MetacognitiveDetail
                              (OrchestratorOutput + VerificationResult)
                                      ↓
                          Educational Display (6-Step Transparency)
                                      ↓
                              Final Assessment
```

### Core Components

1. **Metacognitive Orchestrator** (MetaCheck.py:1239-1318)
   - Coordinates the entire fact-checking workflow
   - Has access to all specialized tools including CRAAP assessor
   - Follows METACOGNITIVE_INSTRUCTIONS for educational transparency
   - Returns structured Pydantic output with full reasoning details

2. **Claim Extractor Agent** (MetaCheck.py:996-1005)
   - Extracts verifiable factual claims from text
   - Filters out opinions and non-verifiable statements

3. **Evidence Gathering & Assessment Tools**
   - **WebSearchTool**: General web search (OpenAI SDK)
   - **CRAAP Assessor Agent** (NEW in v3.0): Evaluates web sources using CRAAP test
   - **WikipediaClient**: Encyclopedia search (MetaCheck.py:792-860)
   - **GoogleFactCheckClient**: Professional fact-checker databases (MetaCheck.py:725-787)

4. **Metacognitive Tracker** (MetaCheck.py:599-744)
   - Tracks reasoning steps
   - Assesses confidence
   - Detects contradictions (with moderate credibility threshold)

5. **Escalation Manager** (MetaCheck.py:647-744)
   - Determines when instructor review is needed
   - Generates guidance notes for human reviewers

6. **Educational Transparency Models** (NEW in v3.0)
   - **SearchQuery**: Documents query generation with reasoning
   - **SourceAssessment**: Complete source evaluation with CRAAP details
   - **VerdictReasoning**: Decision logic with alternatives considered
   - **MetacognitiveDetail**: Full transparency record including limitations

---

## Phase 1: Multi-Agent Fact-Checking

### Goal
Gather evidence from multiple sources and synthesize a verdict for each claim.

### Step-by-Step Process

#### 1. Claim Extraction

**Location**: MetaCheck.py:567-576

```python
claim_extractor = Agent(
    name="claim_extractor",
    instructions="Extract factual claims that can be verified...",
    output_type=ClaimList,
)
```

**Input**: Raw text from user
```
"COVID-19 vaccines are safe and effective. The vaccines contain microchips."
```

**Output**: Structured ClaimList
```python
ClaimList(
    claims=[
        Claim(text="COVID-19 vaccines are safe and effective", worthiness_score=0.9),
        Claim(text="The vaccines contain microchips", worthiness_score=0.8)
    ]
)
```

**Logic**:
- Identifies sentences that make factual assertions
- Filters out opinions ("I think...", "probably...")
- Assigns worthiness_score based on verifiability
- Returns structured data (Pydantic model)

---

#### 2. Evidence Gathering (For Each Claim)

The orchestrator gathers evidence from **3 different sources** for each claim:

##### 2a. Web Search

**Tool**: WebSearchTool (OpenAI SDK)

**What it does**:
- Searches general web for recent information
- Returns URLs, titles, and snippets
- Provides current/breaking information

**Example Query**: "COVID-19 vaccines safe effective"

**Example Results**:
```
- FDA: COVID-19 Vaccine Safety (https://www.fda.gov/...)
- CDC: Vaccine Effectiveness Studies (https://www.cdc.gov/...)
- Mayo Clinic: Vaccine Facts (https://www.mayoclinic.org/...)
```

**Evidence Created**:
```python
Evidence(
    source_name="FDA",
    source_type="web_search",
    url="https://www.fda.gov/vaccines",
    snippet="FDA has determined the vaccines are safe and effective...",
    credibility_score=0.9,
    stance="supports"
)
```

---

##### 2b. Wikipedia Search

**Tool**: wikipedia_search_tool (MetaCheck.py:495-505)
**Client**: WikipediaClient (MetaCheck.py:202-270)

**What it does**:
- Searches Wikipedia using REST API v1
- Retrieves article summaries
- Provides encyclopedic background

**API Endpoints**:
```
Search: https://en.wikipedia.org/w/rest.php/v1/search/page
Summary: https://en.wikipedia.org/api/rest_v1/page/summary/{title}
```

**Example Query**: "COVID-19 vaccine"

**Example Results**:
```
- COVID-19 vaccine (article)
- Vaccine efficacy (article)
- Vaccine safety (article)
```

**Evidence Created**:
```python
Evidence(
    source_name="Wikipedia: COVID-19 vaccine",
    source_type="wikipedia",
    url="https://en.wikipedia.org/wiki/COVID-19_vaccine",
    snippet="COVID-19 vaccines have been shown to be safe and effective...",
    credibility_score=0.8,  # Encyclopedia: generally reliable
    stance="supports"
)
```

---

##### 2c. Fact-Check Database Query

**Tool**: google_fact_check_tool (MetaCheck.py:685-730)
**Client**: GoogleFactCheckClient (MetaCheck.py:135-196)

**What it does**:
- Queries professional fact-checking organizations
- Searches databases from Snopes, PolitiFact, FactCheck.org, etc.
- Returns existing fact-check verdicts

**API Endpoint**:
```
https://factchecktools.googleapis.com/v1alpha1/claims:search
```

**Example Query**: "vaccines microchips"

**Example Results**:
```
- Snopes: "FALSE - No microchips in vaccines"
- PolitiFact: "Pants on Fire - Vaccine microchip claim"
- FactCheck.org: "No evidence of tracking chips"
```

**Evidence Created**:
```python
Evidence(
    source_name="Snopes",
    source_type="fact_check",
    url="https://www.snopes.com/fact-check/...",
    snippet="FALSE: COVID-19 vaccines do not contain microchips",
    credibility_score=0.95,  # Professional fact-checkers: highest credibility
    stance="refutes"
)
```

**Rating Interpretation Logic** (MetaCheck.py:175-188):
```python
def _interpret_rating(rating_text: str) -> str:
    rating_lower = rating_text.lower()
    if any(word in rating_lower for word in ["false", "incorrect", "no evidence"]):
        return "refutes"
    elif any(word in rating_lower for word in ["true", "correct", "confirmed"]):
        return "supports"
    elif any(word in rating_lower for word in ["mixture", "partly", "mostly"]):
        return "neutral"
    else:
        return "unclear"
```

---

#### 3. Verdict Synthesis

**Location**: Orchestrator applies VERDICT_CRITERIA (MetaCheck.py:59-75)

```python
VERDICT_CRITERIA = """
VERDICT TYPES:

1. SUPPORTED: The claim is confirmed by credible evidence
   - Requires: Multiple credible sources (≥0.7) confirm the claim
   - No credible contradictory evidence
   - Evidence directly addresses the core assertion

2. REFUTED: The claim is contradicted by credible evidence
   - Requires: Credible sources (≥0.7) explicitly contradict the claim
   - Evidence provides clear counter-factual information
   - IMPORTANT: Use REFUTED when high-credibility sources (>0.8) refute,
     even if low-credibility sources (<0.7) support

3. INSUFFICIENT: Not enough credible evidence exists
   - Very limited evidence (fewer than 2 sources total)
   - ALL available sources lack credibility (<0.7)
   - Evidence is indirect, vague, or incomplete on ALL sides
   - IMPORTANT: Do NOT use when credible evidence clearly refutes or supports,
     even if some low-credibility sources disagree

4. CONFLICTING: Credible sources disagree on both sides
   - Multiple CREDIBLE sources (≥0.7) present opposing views on BOTH sides
   - Both supporting and refuting sides have credible evidence
   - Credibility and quantity roughly balanced
   - IMPORTANT: Requires genuine conflict between credible sources,
     not low-credibility vs credible sources

5. NEEDS_INSTRUCTOR: Requires expert human judgment
   - Low confidence (<0.6) AND contradictions between credible sources
   - Sensitive or complex topic requiring expert review
   - Evidence is highly technical or specialized

EVIDENCE WEIGHTING RULES:

1. Credibility Thresholds:
   - High-credibility: >0.8 (e.g., fact-checkers at 0.95)
   - Credible: ≥0.7 (e.g., Wikipedia at 0.8, web sources at 0.70)
   - Low-credibility: <0.7 (unreliable or unclear)

2. Weight evidence by credibility score:
   - High-credibility sources (>0.8) have strongest weight
   - Credible sources (≥0.7) dominate verdict over low-credibility sources
   - Compare total credibility weight: sum of credibility scores on each side

3. Decision Priority:
   - If credible sources (≥0.7) clearly support or refute → use SUPPORTED/REFUTED
   - If credible sources conflict → use CONFLICTING
   - Only use INSUFFICIENT when no credible sources exist or all are unclear
   - Example: 1 high-cred refuting (0.95) outweighs multiple low-cred supporting (0.6, 0.5)
"""
```

**Synthesis Logic**:

1. **Organize evidence by stance**:
   ```python
   supporting = [e for e in evidence if e.stance == "supports"]
   refuting = [e for e in evidence if e.stance == "refutes"]
   neutral = [e for e in evidence if e.stance == "neutral"]
   ```

2. **Calculate weighted credibility**:
   ```python
   supporting_weight = sum(e.credibility_score for e in supporting)
   refuting_weight = sum(e.credibility_score for e in refuting)
   ```

3. **Apply decision rules**:
   ```python
   if len(supporting) >= 2 and supporting_weight > refuting_weight * 2:
       verdict = "SUPPORTED"
   elif len(refuting) >= 2 and refuting_weight > supporting_weight * 2:
       verdict = "REFUTED"
   elif len(supporting) > 0 and len(refuting) > 0:
       verdict = "CONFLICTING"
   else:
       verdict = "INSUFFICIENT"
   ```

**Example: "COVID-19 vaccines are safe and effective"**

Evidence collected:
- Web: 3 sources (FDA, CDC, WHO) → all support (credibility: 0.9 each)
- Wikipedia: 1 article → supports (credibility: 0.8)
- Fact-checks: 2 confirmations → support (credibility: 0.95 each)

Calculation:
- Supporting sources: 6
- Supporting weight: 2.7 + 0.8 + 1.9 = 5.4
- Refuting sources: 0
- Refuting weight: 0

**Result**: SUPPORTED (confidence: 0.95)

**Example: "Vaccines contain microchips"**

Evidence collected:
- Web: 2 debunking articles → refute (credibility: 0.7 each)
- Wikipedia: Vaccine misinformation page → refutes (credibility: 0.8)
- Fact-checks: 3 fact-checkers (Snopes, PolitiFact, FactCheck.org) → all refute (credibility: 0.95 each)

Calculation:
- Refuting sources: 6
- Refuting weight: 1.4 + 0.8 + 2.85 = 5.05
- Supporting sources: 0
- Supporting weight: 0

**Result**: REFUTED (confidence: 0.98)

---

#### 4. Structured Output Generation

**Model**: OrchestratorOutput (MetaCheck.py:147-150)

```python
class OrchestratorOutput(BaseModel):
    claim_results: List[VerificationResult]
    summary: str = ""
```

**Each VerificationResult** (MetaCheck.py:111-119):
```python
class VerificationResult(BaseModel):
    claim: str
    verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float  # 0.0 to 1.0
    justification: str
    key_sources: List[str]  # Format: "Source Name [URL]"
    evidence_list: List[Evidence]
    metacognitive_steps: List[MetacognitiveStep]
```

**Why Structured Output?**
- Eliminates text parsing errors (regex failures)
- Type-safe with Pydantic validation
- Predictable format every time
- Handles dynamic number of claims
- Direct access to data fields

---

## Phase 2: Metacognitive Analysis

### Goal
Add self-monitoring, confidence assessment, and reasoning transparency on top of Phase 1 results.

### Step-by-Step Process

#### 1. Confidence Assessment

**Location**: MetacognitiveTracker.assess_confidence() (MetaCheck.py:185-231)

**Purpose**: Calculate how confident we should be in the verdict based on evidence quality.

**Algorithm**:

```python
def assess_confidence(self, verdict: str, evidence_list: List[Evidence]) -> float:
    # Step 1: Separate evidence by stance
    supporting = [e for e in evidence_list if e.stance == "supports"]
    refuting = [e for e in evidence_list if e.stance == "refutes"]

    # Step 2: Calculate weighted credibility
    supporting_weight = sum(e.credibility_score for e in supporting)
    refuting_weight = sum(e.credibility_score for e in refuting)

    # Step 3: Apply verdict-specific logic
    if verdict == "SUPPORTED":
        # More supporting sources = higher confidence
        if len(supporting) >= 3 and supporting_weight > refuting_weight * 2:
            return 0.9  # High confidence
        elif len(supporting) >= 2 and supporting_weight > refuting_weight:
            return 0.75  # Medium-high confidence
        elif len(supporting) >= 1:
            return 0.6  # Medium confidence
        else:
            return 0.4  # Low confidence

    elif verdict == "REFUTED":
        # More refuting sources = higher confidence
        if len(refuting) >= 3 and refuting_weight > supporting_weight * 2:
            return 0.95  # Very high confidence (clear debunk)
        elif len(refuting) >= 2 and refuting_weight > supporting_weight:
            return 0.8  # High confidence
        else:
            return 0.65  # Medium confidence

    elif verdict == "CONFLICTING":
        # Conflicts = lower confidence (capped at 0.6)
        balance = abs(supporting_weight - refuting_weight)
        if balance < 0.5:
            return 0.4  # Very balanced = low confidence
        else:
            return 0.6  # Some imbalance = medium-low confidence

    elif verdict == "INSUFFICIENT":
        # Not enough evidence = low confidence
        return 0.3 + (len(evidence_list) * 0.05)  # Slight boost for more sources

    else:  # NEEDS_INSTRUCTOR
        return 0.5  # Medium confidence - needs expert review
```

**Confidence Scale**:
- **0.9-1.0**: Very high confidence - overwhelming evidence
- **0.8-0.9**: High confidence - clear consensus
- **0.7-0.8**: Medium-high confidence - strong but not overwhelming
- **0.6-0.7**: Medium confidence - decent evidence
- **0.5-0.6**: Medium-low confidence - some uncertainty
- **0.4-0.5**: Low confidence - significant uncertainty
- **0.0-0.4**: Very low confidence - insufficient evidence

**Example Calculation**:

Claim: "COVID-19 vaccines are safe and effective"
- Verdict: SUPPORTED
- Evidence: 3 supporting sources (avg credibility: 0.9)
- Supporting weight: 2.7
- Refuting weight: 0
- Calculation: len(supporting)=3 AND 2.7 > 0*2 → confidence = 0.9

---

#### 2. Contradiction Detection

**Location**: MetacognitiveTracker.detect_contradictions() (MetaCheck.py:233-268)

**Purpose**: Identify when credible sources disagree, which indicates controversy or complexity.

**Algorithm** (Updated with new thresholds):

```python
def detect_contradictions(self, evidence_list: List[Evidence]) -> ContradictionDetection:
    # Step 1: Separate evidence by stance
    supporting = [e for e in evidence_list if e.stance == "supports"]
    refuting = [e for e in evidence_list if e.stance == "refutes"]

    # Step 2: Check if both exist
    if len(supporting) == 0 or len(refuting) == 0:
        return ContradictionDetection(detected=False)

    # Step 3: Filter by credibility tiers
    credible_supporting = [e for e in supporting if e.credibility_score >= 0.7]
    credible_refuting = [e for e in refuting if e.credibility_score >= 0.7]

    moderate_supporting = [e for e in supporting if 0.5 <= e.credibility_score < 0.7]
    moderate_refuting = [e for e in refuting if 0.5 <= e.credibility_score < 0.7]

    # Step 4: Check if contradiction exists (at least moderate credibility on both sides)
    all_supporting = credible_supporting + moderate_supporting
    all_refuting = credible_refuting + moderate_refuting

    if len(all_supporting) == 0 or len(all_refuting) == 0:
        return ContradictionDetection(detected=False)

    # Step 5: Assess severity based on credibility levels
    if len(credible_supporting) >= 2 and len(credible_refuting) >= 2:
        severity = "major"  # Multiple credible sources (≥0.7) on both sides
        description = "Found {n} credible sources supporting and {m} refuting"
    elif len(credible_supporting) >= 1 and len(credible_refuting) >= 1:
        severity = "moderate"  # At least one credible source on each side
        description = "Credible sources disagree (credible ≥0.7 on both sides)"
    else:
        severity = "minor"  # Only moderate credibility sources (0.5-0.7) conflicting
        description = "Sources with moderate credibility disagree"

    # Step 6: List all contradicting sources with credibility scores
    contradicting_sources = [
        f"{e.source_name} (supports, cred={e.credibility_score:.2f})"
        for e in all_supporting
    ] + [
        f"{e.source_name} (refutes, cred={e.credibility_score:.2f})"
        for e in all_refuting
    ]

    return ContradictionDetection(
        detected=True,
        contradicting_sources=contradicting_sources,
        description=description,
        severity=severity
    )
```

**Severity Levels** (Updated):

1. **MAJOR**:
   - **2+ credible sources (≥0.7) on BOTH supporting AND refuting sides**
   - Example: Wikipedia (0.8) + 2 web sources (0.7 each) support, while fact-checker (0.95) refutes
   - Action: Definitely needs expert review

2. **MODERATE**:
   - **At least 1 credible source (≥0.7) on each side**
   - Example: 1 web source (0.7) supports, 1 Wikipedia article (0.8) refutes
   - Action: Investigate further, may need escalation

3. **MINOR**:
   - **Only moderate credibility sources (0.5-0.7) conflicting**
   - Example: Two sources with 0.6 credibility disagree
   - Action: Can likely be ignored, low weight in verdict

**Important**: Sources with credibility <0.5 are ignored in contradiction detection as they are considered unreliable.

**Example** (Updated):

Claim: "Donald Trump raised military recruitment in 2025"

Evidence:
- Supporting: 1 web source (credibility: 0.60) → below 0.7 threshold
- Refuting: 1 fact-checker (credibility: 0.95) → credible
- Neutral: 1 web source (credibility: 0.78)

Result with NEW logic:
```python
ContradictionDetection(
    detected=True,  # Now detects even moderate vs credible conflict
    contradicting_sources=[
        "Supporting Source (supports, cred=0.60)",
        "Fact-Checker (refutes, cred=0.95)"
    ],
    description="Found 1 sources supporting and 1 sources refuting (credible ≥0.7: 1)",
    severity="minor"  # Only moderate credibility on supporting side
)
```

Result with OLD logic (for comparison):
```python
ContradictionDetection(
    detected=False  # Would have missed this because 0.60 < 0.7 threshold
)
```

**Display**:
```
⚠️  CONTRADICTIONS DETECTED
Severity: MINOR
Description: Found 1 sources supporting and 1 sources refuting
  (some with moderate credibility 0.5-0.7)

Conflicting Sources:
  - Supporting Source (supports, cred=0.60)
  - Fact-Checker (refutes, cred=0.95)
```

**Key Improvement**: The new thresholds (0.5-0.7 for moderate, ≥0.7 for credible) catch contradictions even when low-credibility sources conflict with high-credibility sources, preventing INSUFFICIENT verdicts when credible evidence exists.

---

#### 3. Escalation Decision

**Location**: EscalationManager.should_escalate() (MetaCheck.py:340-428)

**Purpose**: Determine if a claim requires expert human review.

**Configuration**:
```python
CONFIDENCE_THRESHOLD = 0.6  # Below this = potential escalation
```

**Sensitivity Analysis** (LLM-Based, Not Hard-Coded):

Instead of hard-coded keywords, MetaCheck uses an LLM-based `sensitivity_analyzer` agent that:
- Analyzes claims for sensitive content using contextual understanding
- Outputs structured data with categories and reasoning
- Considers context (e.g., "vaccines effective" vs "vaccines cause autism" have different sensitivity)

```python
class SensitivityAnalysis(BaseModel):
    is_sensitive: bool
    sensitive_categories: List[str]  # e.g., ["Health & Medical", "Political"]
    reasoning: str  # Why it's sensitive (or not)

# Common categories considered:
# - Health & Medical: Disease, treatment, vaccines, mortality
# - Safety & Security: Violence, crime, terrorism, threats
# - Vulnerable Populations: Children, elderly, abuse
# - Political: Elections, voting, fraud, government
# - Legal: Court cases, allegations, investigations
# - Financial: Scams, fraud, investment risks
# - Religious: Sacred beliefs, religious figures
# - Identity: Race, ethnicity, gender (when divisive)
```

**Decision Logic** (Updated with LLM-based sensitivity):

```python
def should_escalate(self, claim, verdict, confidence, contradiction, evidence_list, sensitivity_analysis):
    reasons = []

    # Rule 1: Explicit NEEDS_INSTRUCTOR verdict
    if verdict == "NEEDS_INSTRUCTOR":
        reasons.append("Verdict explicitly requires specialized expertise")

    # Rule 2: Low confidence + contradictions
    if confidence < CONFIDENCE_THRESHOLD and contradiction.detected:
        reasons.append(f"Low confidence ({confidence:.2f}) combined with contradictory evidence")

    # Rule 3: Low confidence + sensitive topic (LLM-determined)
    if confidence < CONFIDENCE_THRESHOLD and sensitivity_analysis and sensitivity_analysis.is_sensitive:
        categories_str = ", ".join(sensitivity_analysis.sensitive_categories) if sensitivity_analysis.sensitive_categories else "general"
        reasons.append(f"Low confidence ({confidence:.2f}) on sensitive topic ({categories_str})")

    # Rule 4: Major contradictions regardless of confidence
    if contradiction.detected and contradiction.severity == "major":
        reasons.append("Major contradictions detected between credible sources")

    # Rule 5: Insufficient evidence on sensitive claims
    if verdict == "INSUFFICIENT" and len(evidence_list) < 2:
        if sensitivity_analysis and sensitivity_analysis.is_sensitive:
            reasons.append("Insufficient evidence for sensitive claim")

    should_escalate = len(reasons) > 0

    if should_escalate:
        # Generate instructor notes
        instructor_notes = self._generate_instructor_notes(
            claim, verdict, confidence, reasons, evidence_list
        )

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(
            verdict, confidence, contradiction
        )
    else:
        instructor_notes = ""
        suggested_actions = []

    return EscalationDecision(
        should_escalate=should_escalate,
        reasons=reasons,
        instructor_notes=instructor_notes,
        suggested_actions=suggested_actions
    )
```

**Instructor Notes Generation**:
```python
def _generate_instructor_notes(self, claim, verdict, confidence, reasons, evidence_list):
    notes = f"ESCALATION REQUIRED\n\n"
    notes += f"Claim: {claim}\n"
    notes += f"Current Verdict: {verdict}\n"
    notes += f"Confidence: {confidence:.2f}\n\n"
    notes += f"Reasons for Escalation:\n"
    for reason in reasons:
        notes += f"  - {reason}\n"
    notes += f"\nEvidence Summary:\n"
    notes += f"  - Total sources: {len(evidence_list)}\n"
    notes += f"  - Average credibility: {sum(e.credibility_score for e in evidence_list) / len(evidence_list):.2f}\n"
    notes += f"\nThis claim requires careful expert review before final determination."
    return notes
```

**Suggested Actions Generation**:
```python
def _generate_suggested_actions(self, verdict, confidence, contradiction):
    actions = []

    if confidence < 0.5:
        actions.append("Gather additional evidence from authoritative sources")

    if contradiction.severity in ["moderate", "major"]:
        actions.append("Consult domain expert to resolve contradictions")

    if verdict == "NEEDS_INSTRUCTOR":
        actions.append("Route to subject matter expert for specialized review")

    actions.append("Document reasoning and evidence for transparency")

    return actions
```

**Example Escalation**:

Claim: "mRNA vaccines can alter human DNA"
- Verdict: CONFLICTING
- Confidence: 0.55
- Contains keyword: "vaccine" (sensitive)
- Major contradiction detected

Output:
```
🚨 ESCALATION NEEDED

Reasons:
  - Low confidence (0.55) on sensitive topic containing 'vaccine'
  - Major contradictions between highly credible sources

Suggested Actions:
  - Consult molecular biology expert to resolve contradictions
  - Gather additional evidence from peer-reviewed journals
  - Document complete reasoning path for review
  - Route to subject matter expert for specialized review

Instructor Notes:
ESCALATION REQUIRED

Claim: mRNA vaccines can alter human DNA
Current Verdict: CONFLICTING
Confidence: 0.55

Reasons for Escalation:
  - Low confidence (0.55) on sensitive topic containing 'vaccine'
  - Major contradictions between highly credible sources

Evidence Summary:
  - Total sources: 5
  - Average credibility: 0.82

This claim requires careful expert review before final determination.
```

---

#### 4. Reasoning Path Tracking

**Location**: MetacognitiveTracker.add_step() (MetaCheck.py:270-283)

**Purpose**: Create an audit trail showing how the system reached its conclusions.

**Implementation**:

```python
class MetacognitiveStep(BaseModel):
    timestamp: datetime
    agent: str  # Which component took this action
    action: str  # What action was taken
    reasoning: str  # Why this action was taken
    confidence: Optional[float] = None  # Confidence in this step

class MetacognitiveTracker:
    def __init__(self):
        self.steps: List[MetacognitiveStep] = []

    def add_step(self, agent: str, action: str, reasoning: str, confidence: float = None):
        """Log a reasoning step"""
        self.steps.append(MetacognitiveStep(
            timestamp=datetime.now(),
            agent=agent,
            action=action,
            reasoning=reasoning,
            confidence=confidence
        ))

    def get_reasoning_path(self) -> str:
        """Generate human-readable reasoning path"""
        output = "Reasoning Path:\n\n"
        for i, step in enumerate(self.steps, 1):
            output += f"{i}. [{step.agent}] {step.action}\n"
            output += f"   Reasoning: {step.reasoning}\n"
            if step.confidence:
                output += f"   Confidence: {step.confidence:.2f}\n"
            output += "\n"
        return output
```

**Example Usage Throughout Workflow**:

```python
# Step 1: Workflow start
tracker.add_step(
    agent="MetaCheck_System",
    action="Workflow initiated",
    reasoning="Beginning fact-check analysis of 223 character input",
    confidence=1.0
)

# Step 2: Orchestrator start
tracker.add_step(
    agent="Orchestrator",
    action="Coordinating multi-agent fact-checking",
    reasoning="Extracting claims and gathering evidence from multiple sources"
)

# Step 3: Claim extraction complete
tracker.add_step(
    agent="ClaimExtractor",
    action="Claims extracted",
    reasoning="Identified 3 verifiable factual claims",
    confidence=0.95
)

# Step 4: Evidence gathering
tracker.add_step(
    agent="Orchestrator",
    action="Evidence gathering",
    reasoning="Querying web search, Wikipedia, and fact-check databases for Claim 1",
    confidence=0.9
)

# Step 5: Verdict reached
tracker.add_step(
    agent="Orchestrator",
    action="Verdict determined",
    reasoning="Claim 1 SUPPORTED with 6 confirming sources, 0 refuting",
    confidence=0.95
)

# Step 6: Metacognitive analysis
tracker.add_step(
    agent="Metacognitive_Analyzer",
    action="Assessing confidence and contradictions",
    reasoning="Analyzing evidence quality and detecting potential contradictions"
)

# Step 7: Workflow complete
tracker.add_step(
    agent="MetaCheck_System",
    action="Analysis completed",
    reasoning="Processed 3 claims with full evidence and metacognitive assessment",
    confidence=0.88
)
```

**Output**:
```
Reasoning Path:

1. [MetaCheck_System] Workflow initiated
   Reasoning: Beginning fact-check analysis of 223 character input
   Confidence: 1.00

2. [Orchestrator] Coordinating multi-agent fact-checking
   Reasoning: Extracting claims and gathering evidence from multiple sources

3. [ClaimExtractor] Claims extracted
   Reasoning: Identified 3 verifiable factual claims
   Confidence: 0.95

4. [Orchestrator] Evidence gathering
   Reasoning: Querying web search, Wikipedia, and fact-check databases for Claim 1
   Confidence: 0.90

5. [Orchestrator] Verdict determined
   Reasoning: Claim 1 SUPPORTED with 6 confirming sources, 0 refuting
   Confidence: 0.95

6. [Metacognitive_Analyzer] Assessing confidence and contradictions
   Reasoning: Analyzing evidence quality and detecting potential contradictions

7. [MetaCheck_System] Analysis completed
   Reasoning: Processed 3 claims with full evidence and metacognitive assessment
   Confidence: 0.88
```

**Benefits**:
- Complete audit trail
- Transparency for users
- Debugging and improvement
- Trust building through explainability

---

## Phase 3: Educational Transparency (NEW)

### Goal
Provide complete visibility into the AI's reasoning process for educational purposes, showing students HOW AI evaluates information.

### New in v3.0

Phase 3 transforms MetaCheck from a black-box fact-checker into an educational tool by capturing and displaying every reasoning step.

### Step-by-Step Process

#### 1. Search Query Documentation

**Purpose**: Show students what queries the AI generates and WHY

**Model**: SearchQuery (MetaCheck.py:354-364)

```python
class SearchQuery(BaseModel):
    query_text: str  # "Donald Trump military recruitment 2025"
    query_reasoning: str  # "Searching for specific claim about Trump and military in 2025"
    search_strategy: Literal["direct", "broad", "contextual", "fact_check"]
    source_tool: Literal["WebSearchTool", "wikipedia_search_tool", "google_fact_check_tool"]
    results_count: int  # How many results were found
    results_used: int  # How many were actually assessed
```

**Display Example** (Step 0):
```
STEP 0: 🔍 SEARCH STRATEGY
--------------------------------------------------
The AI generated the following search queries:

📌 Query 1: "Donald Trump military recruitment 2025"
   Tool: google_fact_check_tool
   Strategy: fact_check
   Reasoning: Searching for existing fact-checks about Trump raising military recruitment in 2025
   Results found: 10
   Results assessed: 3

📌 Query 2: "US military recruitment increase 2025 Trump administration"
   Tool: WebSearchTool
   Strategy: broad
   Reasoning: Broader search for context about military recruitment trends under Trump
   Results found: 15
   Results assessed: 4
```

**Educational Value**:
- Shows search strategy thinking
- Reveals AI's query formulation process
- Demonstrates different search approaches

---

#### 2. Source-by-Source Assessment Documentation

**Purpose**: Show complete CRAAP test evaluation for each source

**Model**: SourceAssessment (MetaCheck.py:547-576)

```python
class SourceAssessment(BaseModel):
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    title: str

    # CRAAP Test (for web sources)
    craap_assessment: Optional[CRAAPAssessment] = None

    # Relevance Assessment
    relevance_score: float  # 0.0-1.0
    relevance_reasoning: str
    relevance_factors: List[str]  # ["directly addresses claim", "recent"]

    # Stance Determination
    stance: Literal["supports", "refutes", "neutral", "unclear"]
    stance_reasoning: str
    key_quotes: List[str]  # Quotes from source supporting stance

    # Credibility Assessment
    credibility_score: float  # 0.0-1.0
    credibility_reasoning: str
    credibility_factors: List[str]  # ["fact-checker", "authoritative"]
```

**CRAAP Test Breakdown**:
```python
class CRAAPAssessment(BaseModel):
    # Currency: Is the information current?
    currency_score: float  # 0.0-1.0
    currency_notes: str

    # Relevance: Does it address the claim?
    relevance_score: float  # 0.0-1.0
    relevance_notes: str

    # Authority: Is the source credible?
    authority_score: float  # 0.0-1.0
    authority_notes: str

    # Accuracy: Is the information accurate?
    accuracy_score: float  # 0.0-1.0
    accuracy_notes: str

    # Purpose: What is the source's intent?
    purpose_score: float  # 0.0-1.0
    purpose_notes: str

    overall_credibility: float  # Average of above scores
```

**Display Example** (Enhanced Step 1):
```
┌─────────────────────────────────────────────────────────────────┐
│ SOURCE 1: FactCheck.org                                         │
│ Type: fact_check                                                │
└─────────────────────────────────────────────────────────────────┘

🎯 CRAAP TEST ASSESSMENT:
  C - Currency:  0.95/1.0
      Published March 2025, highly current for 2025 claim
  R - Relevance: 0.90/1.0
      Directly addresses the specific claim about Trump and recruitment
  A - Authority: 0.95/1.0
      Established fact-checking organization with editorial standards
  A - Accuracy:  0.90/1.0
      Cites official DoD statistics and expert sources
  P - Purpose:   0.95/1.0
      Nonprofit fact-checking mission, transparent methodology

  📊 OVERALL CRAAP CREDIBILITY: 0.93/1.0

🔍 RELEVANCE ASSESSMENT:
  Score: 0.90/1.0
  Reasoning: Directly addresses Trump military recruitment claim with specific data
  Factors:
    - Directly addresses the core claim
    - Provides specific statistics
    - Recent publication date

📍 STANCE: REFUTES
  Reasoning: Article explicitly states the claim is false with evidence
  Key Quotes:
    - "No evidence of increased military recruitment under Trump in 2025"
    - "DoD data shows recruitment numbers actually declined"

💯 CREDIBILITY SCORE: 0.95/1.0
  Reasoning: Professional fact-checker with high editorial standards
  Factors:
    - Established fact-checking organization
    - Cites authoritative sources (DoD)
```

**Educational Value**:
- Shows systematic source evaluation framework
- Teaches CRAAP test methodology
- Demonstrates critical thinking about sources

---

#### 3. Verdict Decision Documentation

**Purpose**: Show how evidence is weighed and why verdict was chosen

**Model**: VerdictReasoning (MetaCheck.py:578-606)

```python
class VerdictReasoning(BaseModel):
    final_verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float

    # Evidence Weighting
    supporting_sources_count: int
    supporting_weight: float  # Sum of credibility scores
    supporting_key_sources: List[str]

    refuting_sources_count: int
    refuting_weight: float  # Sum of credibility scores
    refuting_key_sources: List[str]

    neutral_sources_count: int
    neutral_weight: float

    unclear_sources_count: int

    # Decision Logic
    primary_reason: str  # "Refuting evidence significantly outweighs supporting"
    decision_rule_applied: str  # "REFUTED: credible sources contradict claim"

    # Alternatives Considered
    alternative_verdicts_considered: List[str]  # ["INSUFFICIENT", "CONFLICTING"]
    why_not_alternatives: str  # Why each was rejected

    # Decisive Factors
    decisive_sources: List[str]  # Sources that tipped the decision
    decisive_factor: str  # What made the verdict clear

    # Confidence Reasoning
    confidence_reasoning: str
    confidence_factors: List[str]
```

**Display Example** (Step 3.5):
```
STEP 3.5: 🤔 VERDICT DECISION PROCESS

📊 EVIDENCE WEIGHTING CALCULATION:
   Supporting sources: 1 sources
   Supporting weight:  0.60 (sum of credibility scores)
   Key sources:
     - Web Source (0.60 credibility)

   Refuting sources:  1 sources
   Refuting weight:   0.95 (sum of credibility scores)
   Key sources:
     - FactCheck.org (0.95 credibility)

   Neutral sources:   1 sources
   Neutral weight:    0.78

   EVIDENCE WEIGHT VISUALIZATION:
   Supporting  [████████████                            ] 0.60
   Refuting    [██████████████████████████████████████  ] 0.95

📋 DECISION RULE APPLIED:
   "REFUTED: High-credibility sources (≥0.7) explicitly contradict the claim"

🔍 VERDICT ALTERNATIVES CONSIDERED:
   ❌ SUPPORTED - Rejected
   ✅ REFUTED - SELECTED
   ❌ INSUFFICIENT - Rejected
   ❌ CONFLICTING - Rejected
   ❌ NEEDS_INSTRUCTOR - Rejected

💡 WHY NOT OTHER VERDICTS:
   - Not SUPPORTED: Refuting weight (0.95) significantly outweighs supporting (0.60)
   - Not INSUFFICIENT: We have credible evidence from fact-checkers
   - Not CONFLICTING: Only one side has high-credibility sources (≥0.8)
   - Not NEEDS_INSTRUCTOR: High confidence (0.85) with clear evidence

🎯 DECISIVE FACTOR:
   High-credibility fact-checker (0.95) refutes claim, outweighing lower-credibility
   supporting source (0.60)

🔒 CONFIDENCE REASONING:
   Confidence: 0.85/1.0
   Factors:
     - High-credibility fact-checker provides clear refutation
     - Low-credibility supporting source doesn't counter strong evidence
     - Neutral source provides additional context
```

**Educational Value**:
- Shows evidence weighting mathematics
- Demonstrates decision logic
- Reveals alternatives considered
- Teaches how confidence is assessed

---

#### 4. AI Limitations Documentation

**Purpose**: Show students where AI might be wrong or uncertain

**Model**: MetacognitiveDetail (MetaCheck.py:608-633)

```python
class MetacognitiveDetail(BaseModel):
    # Search & Sources
    search_queries: List[SearchQuery]
    sources_assessed: List[SourceAssessment]
    sources_rejected: List[RejectedSource]  # Sources found but not used

    # Verdict & Analysis
    verdict_reasoning: Optional[VerdictReasoning]
    contradiction_detection: Optional[ContradictionDetection]
    sensitivity_analysis: Optional[SensitivityAnalysis]
    escalation_decision: Optional[EscalationDecision]

    # Limitations & Uncertainties
    ai_uncertainties: List[str]  # "Couldn't access full article text"
    assumptions_made: List[str]  # "Assumed FactCheck.org has 0.95 credibility"
    potential_weaknesses: List[str]  # "Limited to English sources only"
```

**Display Example** (Step 6):
```
STEP 6: 🔬 AI LIMITATIONS & UNCERTAINTIES

❓ WHAT THE AI COULDN'T DETERMINE:
   1. Could not access full text of paywalled articles
   2. Unable to verify if DoD statistics were the most recent available
   3. Did not have access to classified military recruitment data

🤔 ASSUMPTIONS MADE:
   1. Assumed FactCheck.org has 0.95 credibility based on established reputation
   2. Assumed web search sources have uniform 0.70 credibility
   3. Assumed claim refers to calendar year 2025 (not fiscal year)

⚠️  POTENTIAL WEAKNESSES IN THIS ASSESSMENT:
   1. Limited to English-language sources only
   2. Fact-checker may have bias or limited access to classified data
   3. Web source credibility fixed at 0.70 regardless of actual domain authority
   4. Could not verify if recruitment metrics definition changed over time

📝 METACOGNITIVE SUMMARY:
   This assessment has high confidence (0.85) due to fact-checker evidence, but
   students should note the AI couldn't access primary sources like official DoD
   reports. The verdict relies on secondary fact-checking sources rather than
   original data.
```

**Educational Value**:
- Teaches humility and skepticism
- Shows AI's knowledge boundaries
- Encourages verification of assumptions
- Promotes critical thinking about AI outputs

---

#### 5. Complete Transparency Integration

**Model**: MetacognitiveDetail links all transparency components

**Location**: VerificationResult.metacognitive_detail (MetaCheck.py:270-280)

```python
class VerificationResult(BaseModel):
    claim: str
    verdict: Literal["SUPPORTED", "REFUTED", ...]
    confidence: float
    justification: str
    key_sources: List[str]
    evidence_list: List[Evidence]
    metacognitive_steps: List[MetacognitiveStep]

    # NEW in v3.0: Full educational transparency
    metacognitive_detail: Optional[MetacognitiveDetail] = None
```

**Display Logic**: Enhanced display functions (MetaCheck.py:1425-1767)
- Step 0: Shows search_queries if present
- Step 1: Shows sources_assessed with full CRAAP details
- Step 3.5: Shows verdict_reasoning if present
- Step 6: Shows ai_uncertainties, assumptions_made, potential_weaknesses

**Educational Flow**:
```
User Query
    ↓
Step 0: Search Strategy (What queries? Why?)
    ↓
Step 1: Source-by-Source Assessment (CRAAP test for each)
    ↓
Step 2: Evidence Summary (Key findings)
    ↓
Step 3: Contradictions (If detected)
    ↓
Step 3.5: Verdict Decision Process (NEW - How verdict was chosen)
    ↓
Step 4: Escalation (If needed)
    ↓
Step 5: Reasoning Path (Audit trail)
    ↓
Step 6: AI Limitations (NEW - What AI couldn't determine)
    ↓
Final Verdict with Complete Transparency
```

---

### Orchestrator Instructions

**METACOGNITIVE_INSTRUCTIONS** (MetaCheck.py:232-338) provides detailed requirements to the orchestrator:

**5 Educational Phases**:

1. **Query Generation Phase**
   - Document what query you're generating
   - Explain WHY you chose those terms
   - Specify search strategy

2. **Evidence Assessment Phase**
   - Call CRAAP assessor for web sources
   - Document relevance, stance, credibility
   - Preserve key quotes from sources

3. **Verdict Decision Phase**
   - Calculate evidence weights
   - List all alternatives considered
   - Explain why each was selected/rejected
   - Identify decisive factors

4. **Uncertainty Acknowledgment Phase**
   - List what you couldn't determine
   - Document assumptions made
   - Identify potential weaknesses

5. **MetacognitiveDetail Population**
   - Populate all fields of MetacognitiveDetail
   - Ensure educational transparency

**Result**: Orchestrator now documents its complete reasoning process for educational purposes.

---

## Complete Workflow

### End-to-End Example

**User Input**:
```python
text = """
COVID-19 vaccines have been proven safe and effective by multiple health organizations.
The vaccines contain microchips to track people.
Bill Gates wants to reduce the world population through vaccination.
"""

result = await verify_claims(text, verbose=True)
```

### Step-by-Step Execution

#### **Step 1: Initialization** (0.1 seconds)
```python
# Create trackers
tracker = MetacognitiveTracker()
escalation_mgr = EscalationManager()

# Log start
tracker.add_step(
    agent="MetaCheck_System",
    action="Workflow initiated",
    reasoning="Beginning fact-check analysis of 223 character input",
    confidence=1.0
)
```

#### **Step 2: Launch Orchestrator** (0.2 seconds)
```python
result = await Runner.run(
    orchestrator,
    prompt="Analyze this text and fact-check all claims...",
    max_turns=30
)
```

#### **Step 3: Extract Claims** (2-3 seconds)
Orchestrator calls `claim_extractor` tool:

**Tool Input**: Full text
**Tool Output**:
```python
ClaimList(
    claims=[
        Claim(text="COVID-19 vaccines have been proven safe and effective by multiple health organizations", worthiness_score=0.9),
        Claim(text="The vaccines contain microchips to track people", worthiness_score=0.85),
        Claim(text="Bill Gates wants to reduce the world population through vaccination", worthiness_score=0.8)
    ],
    extraction_method="AI claim extractor"
)
```

#### **Step 4: Evidence Gathering for Claim 1** (10-15 seconds)

##### Web Search
**Query**: "COVID-19 vaccines safe effective health organizations"
**Results**: 10 URLs
**Top 3**:
1. FDA: Vaccine Safety (credibility: 0.9, stance: supports)
2. CDC: Effectiveness Studies (credibility: 0.9, stance: supports)
3. WHO: Vaccine Approval (credibility: 0.85, stance: supports)

##### Wikipedia Search
**Query**: "COVID-19 vaccine safety efficacy"
**Results**: 2 articles
1. COVID-19 vaccine (credibility: 0.8, stance: supports)
2. Vaccine efficacy (credibility: 0.8, stance: supports)

##### Fact-Check Query
**Query**: "COVID-19 vaccines safe effective"
**Results**: 3 fact-checks
1. FactCheck.org: "TRUE" (credibility: 0.95, stance: supports)
2. Snopes: "CORRECT" (credibility: 0.95, stance: supports)
3. PolitiFact: "TRUE" (credibility: 0.95, stance: supports)

**Total Evidence**: 8 sources, all supporting, average credibility: 0.88

#### **Step 5: Verdict Synthesis for Claim 1** (1 second)
```python
# Apply VERDICT_CRITERIA
supporting_count = 8
supporting_weight = 7.0
refuting_count = 0
refuting_weight = 0

# Decision: 8 sources >= 2, weight 7.0 >> 0
verdict = "SUPPORTED"
confidence = 0.95  # High confidence due to overwhelming evidence
```

#### **Step 6: Repeat for Claims 2 and 3** (20-25 seconds each)

**Claim 2**: "The vaccines contain microchips"
- Web: 3 debunking articles (refute)
- Wikipedia: Vaccine misinformation page (refutes)
- Fact-checks: All refute (Snopes, PolitiFact, FactCheck.org)
- **Verdict**: REFUTED (confidence: 0.98)

**Claim 3**: "Bill Gates wants to reduce population"
- Web: Mixed articles, mostly debunking
- Wikipedia: Misquoted statements article (refutes)
- Fact-checks: All refute conspiracy theory
- **Verdict**: REFUTED (confidence: 0.96)

#### **Step 7: Structured Output Creation** (0.1 seconds)
```python
orchestrator_output = OrchestratorOutput(
    claim_results=[
        VerificationResult(
            claim="COVID-19 vaccines have been proven safe...",
            verdict="SUPPORTED",
            confidence=0.95,
            justification="Multiple authoritative sources confirm...",
            key_sources=["FDA [https://...]", "CDC [https://...]"],
            evidence_list=[...8 Evidence objects...],
            metacognitive_steps=[]
        ),
        VerificationResult(
            claim="The vaccines contain microchips...",
            verdict="REFUTED",
            confidence=0.98,
            justification="Professional fact-checkers unanimously debunk...",
            key_sources=["Snopes [https://...]", "FactCheck.org [https://...]"],
            evidence_list=[...6 Evidence objects...],
            metacognitive_steps=[]
        ),
        VerificationResult(
            claim="Bill Gates wants to reduce population...",
            verdict="REFUTED",
            confidence=0.96,
            justification="Claim misrepresents Gates's statements...",
            key_sources=["Wikipedia [https://...]", "Business Insider [https://...]"],
            evidence_list=[...5 Evidence objects...],
            metacognitive_steps=[]
        )
    ],
    summary="Analyzed 3 claims with comprehensive evidence gathering"
)
```

#### **Step 8: Phase 2 Analysis - Confidence Assessment** (0.5 seconds)
```python
for claim_result in claim_results:
    # Already calculated by orchestrator
    confidence = claim_result.confidence
    # Claim 1: 0.95
    # Claim 2: 0.98
    # Claim 3: 0.96
```

#### **Step 9: Phase 2 Analysis - Contradiction Detection** (0.5 seconds)
```python
for claim_result in claim_results:
    contradiction = tracker.detect_contradictions(claim_result.evidence_list)

# Claim 1: No contradictions (all support)
# Claim 2: No contradictions (all refute)
# Claim 3: No contradictions (all refute)
```

#### **Step 10: Phase 2 Analysis - Escalation Check** (0.5 seconds)
```python
for claim_result in claim_results:
    escalation = escalation_mgr.should_escalate(
        claim=claim_result.claim,
        verdict=claim_result.verdict,
        confidence=claim_result.confidence,
        contradiction=contradiction,
        evidence_list=claim_result.evidence_list
    )

# Claim 1: No escalation (high confidence, no contradictions)
# Claim 2: No escalation (very high confidence, clear refutation)
# Claim 3: No escalation (high confidence, clear refutation)
```

#### **Step 11: Display Results** (0.1 seconds)

**Fact-Checking Report**:
```
======================================================================
FACT-CHECKING REPORT
======================================================================

## Claim 1
**Claim:** COVID-19 vaccines have been proven safe and effective by multiple health organizations.

**Verdict:** SUPPORTED
**Confidence:** 0.95

**Justification:** Multiple authoritative public health sources—including the FDA, CDC, EMA and WHO—have evaluated clinical trial data and monitored real-world use, concluding COVID‑19 vaccines are both safe and effective.

**Key Sources:**
  - FDA emergency use authorization [https://www.fda.gov/...]
  - CDC effectiveness studies [https://www.cdc.gov/...]
  - FactCheck.org confirmation [https://www.factcheck.org/...]

----------------------------------------------------------------------

## Claim 2
**Claim:** The vaccines contain microchips to track people.

**Verdict:** REFUTED
**Confidence:** 0.98

**Justification:** Multiple reliable fact‑checking organizations and health authorities confirm there is no evidence COVID‑19 vaccines contain microchips or tracking devices. The microchip conspiracy is physically and technologically implausible.

**Key Sources:**
  - Snopes debunk [https://www.snopes.com/...]
  - FactCheck.org debunk [https://www.factcheck.org/...]
  - CDC myth-buster [https://www.cdc.gov/...]

----------------------------------------------------------------------

## Claim 3
**Claim:** Bill Gates wants to reduce the world population through vaccination.

**Verdict:** REFUTED
**Confidence:** 0.96

**Justification:** This claim misrepresents Bill Gates' 2010 TED talk, where he stated that improved healthcare—including vaccines—can lead to lower child mortality, which typically correlates with reduced birth rates. Multiple fact-checks confirm the conspiracy version is false.

**Key Sources:**
  - Wikipedia misquote article [https://en.wikipedia.org/...]
  - Business Insider Gates interview [https://www.businessinsider.com/...]

----------------------------------------------------------------------
```

**Metacognitive Analysis**:
```
======================================================================
METACOGNITIVE ANALYSIS (Phase 2)
======================================================================

Claim 1: COVID-19 vaccines have been proven safe and effective by multiple health organizations.
  Verdict: SUPPORTED
  Confidence: 0.95

Claim 2: The vaccines contain microchips to track people.
  Verdict: REFUTED
  Confidence: 0.98

Claim 3: Bill Gates wants to reduce the world population through vaccination.
  Verdict: REFUTED
  Confidence: 0.96

Reasoning Path:

1. [MetaCheck_System] Workflow initiated
   Reasoning: Beginning fact-check analysis of 223 character input
   Confidence: 1.00

2. [Orchestrator] Coordinating multi-agent fact-checking
   Reasoning: Extracting claims and gathering evidence from multiple sources

3. [Orchestrator] Fact-checking completed
   Reasoning: Analyzed 3 claims with evidence from multiple sources
   Confidence: 0.85

4. [Metacognitive_Analyzer] Assessing confidence and contradictions
   Reasoning: Analyzing evidence quality and detecting potential contradictions

======================================================================
ASSESSMENT COMPLETE
======================================================================
Total claims processed: 3
Average confidence: 0.96
Generated at: 2025-10-29 10:00:10
```

#### **Step 12: Return Final Assessment** (0.1 seconds)
```python
assessment = FinalAssessment(
    input_text=text,
    total_claims=3,
    claim_results=claim_results,
    overall_credibility="Average Confidence: 0.96",
    generated_at=datetime.now()
)

return assessment
```

**Total Time**: ~60-80 seconds (mostly evidence gathering API calls)

---

## Data Models

### Core Models (MetaCheck.py:78-150)

#### Claim
```python
class Claim(BaseModel):
    text: str
    worthiness_score: float = Field(ge=0.0, le=1.0, default=0.8)
    extracted_at: datetime = Field(default_factory=datetime.now)
```

#### Evidence
```python
class Evidence(BaseModel):
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.7)
    credibility_score: float = Field(ge=0.0, le=1.0, default=0.7)
    stance: Optional[Literal["supports", "refutes", "neutral", "unclear"]] = None
```

**Credibility Scores** (Fixed by Source Type):
- **0.95**: Professional fact-checkers (Snopes, PolitiFact, FactCheck.org) - FIXED
- **0.80**: Wikipedia (encyclopedia, community-edited) - FIXED
- **0.70**: All web search sources (regardless of domain) - FIXED

**Credibility Tiers**:
- **High-credibility (>0.8)**: Fact-checkers (0.95)
- **Credible (≥0.7)**: Wikipedia (0.8), Web sources (0.70)
- **Moderate (0.5-0.7)**: Sources below credible threshold but still relevant
- **Low (<0.5)**: Unreliable sources (ignored in analysis)

**Important**: Web search credibility is **fixed at 0.70** for all sources because the LLM cannot reliably assess website credibility from URL + snippet alone without reading full content.

#### VerificationResult
```python
class VerificationResult(BaseModel):
    claim: str
    verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str
    key_sources: List[str]
    evidence_list: List[Evidence] = []
    metacognitive_steps: List[MetacognitiveStep] = []
    metacognitive_detail: Optional[MetacognitiveDetail] = None  # NEW in v3.0
```

#### MetacognitiveStep
```python
class MetacognitiveStep(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str
    action: str
    reasoning: str
    confidence: Optional[float] = None
```

#### ContradictionDetection
```python
class ContradictionDetection(BaseModel):
    detected: bool = False
    contradicting_sources: List[str] = []
    description: str = ""
    severity: Literal["minor", "moderate", "major"] = "minor"
```

#### EscalationDecision
```python
class EscalationDecision(BaseModel):
    should_escalate: bool
    reasons: List[str]
    instructor_notes: str
    suggested_actions: List[str] = []
```

#### OrchestratorOutput
```python
class OrchestratorOutput(BaseModel):
    claim_results: List[VerificationResult]
    summary: str = ""
```

#### FinalAssessment
```python
class FinalAssessment(BaseModel):
    input_text: str
    total_claims: int
    claim_results: List[VerificationResult]
    overall_credibility: str
    generated_at: datetime = Field(default_factory=datetime.now)
```

---

### Educational Transparency Models (NEW in v3.0)

These models capture complete AI reasoning for educational purposes.

#### SearchQuery (MetaCheck.py:354-364)
```python
class SearchQuery(BaseModel):
    """Records AI's search strategy for transparency"""
    query_text: str
    query_reasoning: str  # WHY this query was generated
    search_strategy: Literal["direct", "broad", "contextual", "fact_check"]
    source_tool: Literal["WebSearchTool", "wikipedia_search_tool", "google_fact_check_tool"]
    timestamp: datetime = Field(default_factory=datetime.now)
    results_count: int = 0  # How many results found
    results_used: int = 0   # How many were assessed
```

**Purpose**: Documents what queries AI generates and the reasoning behind them.

**Educational Use**: Students see how AI formulates search queries.

---

#### CRAAPAssessment (MetaCheck.py:205-230)
```python
class CRAAPAssessment(BaseModel):
    """Complete CRAAP test for source evaluation"""
    # Currency: Is the information current?
    currency_score: float = Field(ge=0.0, le=1.0)
    currency_notes: str

    # Relevance: Does it address the claim?
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_notes: str

    # Authority: Is the source credible?
    authority_score: float = Field(ge=0.0, le=1.0)
    authority_notes: str

    # Accuracy: Is the information accurate?
    accuracy_score: float = Field(ge=0.0, le=1.0)
    accuracy_notes: str

    # Purpose: What is the source's intent?
    purpose_score: float = Field(ge=0.0, le=1.0)
    purpose_notes: str

    # Overall credibility (average of above)
    overall_credibility: float = Field(ge=0.0, le=1.0)
```

**Purpose**: Systematic framework for evaluating web sources.

**Educational Use**: Teaches CRAAP test methodology with concrete examples.

---

#### RejectedSource (MetaCheck.py:543-547)
```python
class RejectedSource(BaseModel):
    """A source that was found but not used"""
    url: str
    reason: str  # Why it was rejected (e.g., "not relevant", "duplicate")
```

**Purpose**: Shows students what sources were excluded and why.

**Educational Use**: Demonstrates source filtering and selection criteria.

---

#### SourceAssessment (MetaCheck.py:549-576)
```python
class SourceAssessment(BaseModel):
    """Detailed assessment of a single source"""
    source_name: str
    source_type: Literal["fact_check", "wikipedia", "web_search"]
    url: str
    title: str = ""

    # CRAAP Test (for web sources)
    craap_assessment: Optional[CRAAPAssessment] = None

    # Relevance
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_reasoning: str
    relevance_factors: List[str] = []

    # Stance
    stance: Literal["supports", "refutes", "neutral", "unclear"]
    stance_reasoning: str
    key_quotes: List[str] = []

    # Credibility
    credibility_score: float = Field(ge=0.0, le=1.0)
    credibility_reasoning: str
    credibility_factors: List[str] = []

    # Metadata
    snippet: str
    publication_date: Optional[str] = None
    author: Optional[str] = None
```

**Purpose**: Complete transparency for each source evaluated.

**Educational Use**: Shows students the complete evaluation process for each source, including CRAAP test, relevance assessment, stance determination, and credibility scoring.

---

#### VerdictReasoning (MetaCheck.py:578-606)
```python
class VerdictReasoning(BaseModel):
    """Detailed reasoning for verdict decision"""
    final_verdict: Literal["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]
    confidence: float = Field(ge=0.0, le=1.0)

    # Evidence Weighting
    supporting_sources_count: int
    supporting_weight: float  # Sum of credibility scores
    supporting_key_sources: List[str] = []

    refuting_sources_count: int
    refuting_weight: float  # Sum of credibility scores
    refuting_key_sources: List[str] = []

    neutral_sources_count: int
    neutral_weight: float

    unclear_sources_count: int

    # Decision Logic
    primary_reason: str
    decision_rule_applied: str

    # Alternatives Considered
    alternative_verdicts_considered: List[str] = []
    why_not_alternatives: str = ""

    # Decisive Factors
    decisive_sources: List[str] = []
    decisive_factor: str

    # Confidence Reasoning
    confidence_reasoning: str
    confidence_factors: List[str] = []
```

**Purpose**: Shows complete decision logic for reaching verdict.

**Educational Use**: Teaches evidence weighting, decision rules, and why alternatives were rejected. Shows mathematics behind confidence scores.

---

#### MetacognitiveDetail (MetaCheck.py:608-633)
```python
class MetacognitiveDetail(BaseModel):
    """Complete metacognitive record for one claim - full transparency"""
    claim: str

    # Search Strategy
    search_queries: List[SearchQuery] = []
    search_strategy_summary: str = ""
    sources_found: int = 0

    # Source Assessment
    sources_assessed: List[SourceAssessment] = []
    sources_rejected: List[RejectedSource] = []

    # Analysis Results
    contradiction_detection: Optional[ContradictionDetection] = None
    verdict_reasoning: Optional[VerdictReasoning] = None
    sensitivity_analysis: Optional[SensitivityAnalysis] = None
    escalation_decision: Optional[EscalationDecision] = None

    # AI Limitations & Uncertainties
    ai_uncertainties: List[str] = []  # What AI couldn't determine
    assumptions_made: List[str] = []  # What AI assumed
    potential_weaknesses: List[str] = []  # Where assessment might be wrong

    # Summary
    total_assessment_time: Optional[float] = None
    metacognitive_summary: str = ""
```

**Purpose**: Master record linking all transparency components for one claim.

**Educational Use**: Complete transparency record showing search strategy, source assessments, decision logic, and AI limitations. This is the top-level educational transparency object that gets displayed in Steps 0, 1, 3.5, and 6.

---

## Installation

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)
- API Keys:
  - OpenAI API key (required)
  - Google Fact Check API key (optional but recommended)
  - Wikipedia access token (optional)

### Setup Steps

1. **Clone the repository**:
```bash
cd /path/to/metacog-agent
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
openai-agents-sdk>=0.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
asyncio
```

4. **Configure API keys**:

Create `.env` file:
```bash
# Required
OPENAI_API_KEY=sk-...your-key-here

# Optional (but recommended)
GOOGLE_FACT_CHECK_API_KEY=AIza...your-key-here

# Optional
WIKIPEDIA_ACCESS_TOKEN=your-token-here
```

**Getting API Keys**:
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Fact Check**: https://console.cloud.google.com/ → Enable Fact Check Tools API
- **Wikipedia**: https://api.wikimedia.org/ (not required for basic usage)

---

## Usage

### Basic Usage

```python
import asyncio
from MetaCheck import verify_claims

async def main():
    text = """
    COVID-19 vaccines have been proven safe and effective.
    The vaccines contain microchips to track people.
    """

    result = await verify_claims(text, verbose=True)

    print(f"Total claims: {result.total_claims}")
    print(f"Overall credibility: {result.overall_credibility}")

asyncio.run(main())
```

### Command Line Usage

```bash
# Run with default test case
python MetaCheck.py

# Run in virtual environment
source venv/bin/activate
python MetaCheck.py
```

### Programmatic Usage

```python
from MetaCheck import verify_claims, FinalAssessment, VerificationResult
import asyncio

async def analyze_text(text: str) -> FinalAssessment:
    """Analyze text and return structured results"""
    result = await verify_claims(text, verbose=False)
    return result

# Access individual claims
async def get_claim_verdicts(text: str) -> dict:
    """Get verdicts for all claims"""
    result = await verify_claims(text, verbose=False)

    verdicts = {}
    for claim_result in result.claim_results:
        verdicts[claim_result.claim] = {
            'verdict': claim_result.verdict,
            'confidence': claim_result.confidence,
            'sources': claim_result.key_sources
        }

    return verdicts

# Usage
text = "COVID-19 vaccines are safe and effective."
verdicts = asyncio.run(get_claim_verdicts(text))
print(verdicts)
```

### Advanced Usage: Custom Thresholds

```python
from MetaCheck import EscalationManager

# Customize escalation thresholds
escalation_mgr = EscalationManager()
escalation_mgr.CONFIDENCE_THRESHOLD = 0.7  # Require higher confidence
escalation_mgr.SENSITIVE_KEYWORDS.append("your_custom_keyword")

# Use in verify_claims (would require code modification)
```

---

## Configuration

### Environment Variables

**Required**:
```bash
OPENAI_API_KEY=sk-...  # OpenAI API key for agents SDK
```

**Optional**:
```bash
GOOGLE_FACT_CHECK_API_KEY=AIza...  # Google Fact Check Tools API
WIKIPEDIA_ACCESS_TOKEN=...          # Wikipedia OAuth token
```

### Verdict Criteria (MetaCheck.py:59-75)

You can customize verdict logic by modifying `VERDICT_CRITERIA`:

```python
VERDICT_CRITERIA = """
SUPPORTED: 2+ credible sources confirm (customizable threshold)
REFUTED: 2+ credible sources contradict
INSUFFICIENT: Fewer than 2 credible sources
CONFLICTING: Credible sources disagree
NEEDS_INSTRUCTOR: Requires expert judgment
"""
```

### Confidence Thresholds

Modify in `MetacognitiveTracker.assess_confidence()` (MetaCheck.py:185-231):

```python
# Example: Lower threshold for SUPPORTED verdict
if len(supporting) >= 1:  # Changed from 2
    return 0.7
```

### Escalation Settings

Modify in `EscalationManager` (MetaCheck.py:292-293):

```python
CONFIDENCE_THRESHOLD = 0.6  # Lower = more escalations
SENSITIVE_KEYWORDS = [...]  # Add custom keywords
```

---
