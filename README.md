# MetaCheck: Building an Educational AI Fact-Checker for Teaching Critical Thinking

**Subtitle:** A multi-agent system that teaches learners how to verify information, not just what to believe

---

## Table of Contents

1. Introduction
2. Claim Extraction: From Text to Verifiable Statements
3. The Verification Pipeline: Multi-Agent Evidence Gathering
4. Educational Design: Learning Through Comparison

---

## 1. Introduction

_(Already written by user)_

Disinformation and fake news have become a global problem. The advancements in technology, in particular, artificial intelligence, have paved the way for creating and promoting disinformation via a myriad of ways.

Disinformation can mislead people, shape public opinion, and weaken trust in institutions, especially during important events and crises. Higher education institutions (HEIs) are especially exposed to disinformation because students rely heavily on online information for learning, research, and everyday decisions. Therefore, both students and teachers should be equipped with the capabilities of assessing information.

While AI can be used for creating and promoting disinformation, for instance, via fake images and videos, synthetic voice, and online bots, among others, it can also be used to assess information and detect disinformation.

That said, using AI for disinformation detection also requires careful design because these models can produce confident but incorrect statements. Therefore, the AI literacy for disinformation should be focused on teaching learners what AI tools can and cannot do, how to verify AI-generated answers with independent sources, and how to document and reflect on their verification steps.

In this article, we will develop an AI tool, MetaCheck, an educational fact-checking tool designed to help learners and educators evaluate information critically. Unlike commercial fact-checkers, MetaCheck's primary goal is educational transparency, demonstrating how AI systems verify claims, not just what verdict they reach.

**MetaCheck:**
- Extracts verifiable claims from text
- Searches the web, Wikipedia, and fact-check sources
- Classifies domain credibility via a configurable taxonomy
- Weighs evidence and issues structured verdicts (Refuted, Supported, Insufficient Information) with confidence scores
- Highlights full metacognitive detail for learners (search strategy, stance, uncertainties, assumptions, verdict reasoning)

The tool lets users first add their own assessment for a verification task, then use AI to perform the same verification, and compare their assessment with AI's. This way, the tool not only serves as an information checker, but also teaches learners how to assess information and how to improve their metacognitive process for information assessment.

The tool uses a multi-agentic approach to run the above-mentioned workflow. The complete workflow is shown in the figure below.

The tool extracts verifiable claims from the text and lets the user select what claims they want to verify. It then creates as many parallel agents as there are claims. Each agent runs three parallel tools: web search, Wikipedia search, and fact-check sources search. An aggregator aggregates the complete evidence and generates the final verdict.

Let's dive in.

---

## 2. Claim Extraction

Not every sentence in a text is worth verifying. MetaCheck therefore begins by identifying only the statements that are specific, falsifiable, and require consulting external sources to confirm or refute.

The user pastes any free-form text — a news article, a social media post, a research summary, or a student reading passage. Claim extraction is handled by the agent defined in `backend/app/agents.py`:

```python
# backend/app/agents.py

claim_extractor = Agent(
    name="claim_extractor",
    instructions=EXTRACTION_INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ClaimList,
)
```

The agent is driven by `EXTRACTION_INSTRUCTIONS` (`backend/app/core/constants.py`) that instructs the model to behave like a professional fact-checker. The key criteria a statement must satisfy to be extracted as a claim are:

1. **Falsifiable** — it can be proven wrong
2. **Specific** — it contains concrete details (numbers, dates, names, locations)
3. **Contextualized** — it is tied to an entity, time, or place
4. **Externally verifiable** — it requires consulting sources beyond general knowledge

The prompt also instructs the agent to split compound sentences into individual claims when each fact requires different evidence. 

The agent returns a structured `ClaimList` object (`backend/app/core/models.py`), where each item is a `Claim`:

```python
# backend/app/core/models.py

class Claim(BaseModel):
    text: str
    worthiness_score: float = Field(ge=0.0, le=1.0, default=0.8)
    extracted_at: datetime = Field(default_factory=datetime.now)
    ...
```

Each extracted claim carries a `worthiness_score` between 0.0 and 1.0, assigned by the LLM during extraction. The user then selects which claim(s) to send to the verification pipeline. 

The figure below shows the full claim extraction flow.

```mermaid
flowchart TD
    A([📄 Input Text]) --> B

    subgraph B[" Claim Extraction Agent "]
        direction TB
        B1[Parse text with<br/>EXTRACTION_INSTRUCTIONS prompt]
        B2[Apply extraction criteria:<br/>Falsifiable · Specific · Contextualized · Verifiable]
        B3[Split compound<br/>sentences into atomic claims]
        B4[Score each claim<br/>by worthiness 0.0 – 1.0]
        B1 --> B2 --> B3 --> B4
    end

    B --> C[ClaimList ranked by worthiness]

    C --> D{👤 User selects<br/>claims to verify}

    D --> E1[✅ Claim 1<br/>worthiness 0.92]
    D --> E2[✅ Claim 2<br/>worthiness 0.85]
    D --> E3[✅ Claim 3<br/>worthiness 0.78]

    E1 --> F([➡️ Verification Pipeline])
    E2 --> F
    E3 --> F

    style A fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style B fill:#f0fdf4,stroke:#22c55e,color:#14532d
    style C fill:#fefce8,stroke:#eab308,color:#713f12
    style D fill:#fdf4ff,stroke:#a855f7,color:#581c87
    style E1 fill:#dcfce7,stroke:#16a34a,color:#14532d
    style E2 fill:#dcfce7,stroke:#16a34a,color:#14532d
    style E3 fill:#dcfce7,stroke:#16a34a,color:#14532d
    style F fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
```


---

## 3. The Verification Pipeline: Multi-Agent Evidence Gathering

Once the user selects claims, MetaCheck launches a parallel verification pipeline with one independent agent per claim, each gathering evidence using three tools simultaneously and producing a structured verdict. 

### 3.1. Parallel Agent Creation

MetaCheck creates one orchestrator agent per selected claim and executes them all in parallel. Since the agents communicate no information with each other during evidence gathering, running them in parallel results in a much faster workflow.

The agent is defined once in `backend/app/core/agents.py` and executed once per claim:

```python
# backend/app/core/agents.py

orchestrator = Agent(
    name="metacognitive_orchestrator",
    model=MODEL_NAME,
    instructions=f"""Fact-check orchestrator. For each claim:
1. Use comprehensive_evidence_tool to gather ALL evidence
   (Tavily web search + Wikipedia + Google Fact Check) in parallel
2. For each Evidence object, analyze stance:
   - Web / Wikipedia: set stance based on snippet content
   - Fact check: stance set by rating interpretation
3. Apply verdict criteria:
   - SUPPORTED: Multiple credible sources (≥0.7) confirm, no contradictions
   - REFUTED: Credible sources (≥0.7) explicitly contradict
   - INSUFFICIENT_INFORMATION: <2 sources OR all <0.7 credibility
   - CONFLICTING_EVIDENCE: Credible sources disagree on both sides
4. Return VerificationResult with verdict, confidence (0–1),
   justification, key_sources, evidence_list
""",
    tools=[comprehensive_evidence_tool],
    output_type=OrchestratorOutput,
)
```

The spawning happens in `backend/app/core/workflow.py`, where a task is created for each selected claim and all tasks are handed to `asyncio.gather()`:

```python
# backend/app/core/workflow.py

semaphore = asyncio.Semaphore(int(os.getenv("METACHECK_MAX_CONCURRENCY", "5")))

async def analyze_claim(claim_text: str):
    async with semaphore:
        agent_result = await Runner.run(
            orchestrator,
            (
                f"{mode_instruction}\n"
                "Use comprehensive_evidence_tool to gather ALL evidence in one parallel call.\n"
                f"Claim to verify: {claim_text}"
            ),
            max_turns=5,
        )
        ...

# One task per claim — all run in parallel
claim_tasks = [analyze_claim_with_timeout(claim) for claim in claim_texts]
claim_results = await asyncio.gather(*claim_tasks)
```

A semaphore bounds the maximum number of concurrently running agents (default: 5, configurable via `METACHECK_MAX_CONCURRENCY`), and each agent is wrapped in a timeout of 90 seconds (`per_claim_timeout_seconds` in `backend/app/core/tool_settings.py`) to prevent runaway calls.

```mermaid
flowchart TD
    A([✅ Selected Claims]) --> B

    subgraph B["workflow.py — asyncio.gather()"]
        direction LR
        T1["analyze_claim(claim 1)"]
        T2["analyze_claim(claim 2)"]
        T3["analyze_claim(claim 3)"]
    end

    B --> C1[orchestrator\nAgent 1]
    B --> C2[orchestrator\nAgent 2]
    B --> C3[orchestrator\nAgent 3]

    C1 --> R([🗂️ claim_results])
    C2 --> R
    C3 --> R

    style A fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style B fill:#f0fdf4,stroke:#22c55e,color:#14532d
    style C1 fill:#fefce8,stroke:#eab308,color:#713f12
    style C2 fill:#fefce8,stroke:#eab308,color:#713f12
    style C3 fill:#fefce8,stroke:#eab308,color:#713f12
    style R fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
```

### 3.2. Parallel Evidence Gathering

#### 3.2.1. Three Parallel Tools Per Agent
- Tavily Web Search
- Wikipedia Search API
- Google Fact Check API

#### 3.2.2. Tool Execution Pattern

#### 3.2.6. Evidence Aggregation

### 3.3. Domain Credibility Classification

#### 3.3.1. Configurable Taxonomy Structure

#### 3.3.2. Domain Categories and Weights

#### 3.3.3. Domain Matching Algorithm

#### 3.3.4. Applying Credibility Weights

### 3.4. Verdict Generation

#### 3.4.1. LLM Reasoning with Evidence

#### 3.4.2. Verdict Categories

#### 3.4.3. Confidence Scoring Logic

#### 3.4.4. Metacognitive Detail (Comprehensive Mode)

---

## 4. Educational Design: Learning Through Comparison

### 4.1. Student Self-Assessment

#### 4.1.1. Assessment Interface

#### 4.1.2. Guided Assessment Framework

### 4.2. Side-by-Side Comparison

#### 4.2.1. Comparison Interface Design

#### 4.2.2. What Gets Compared

### 4.3. AI-Generated Learning Feedback

#### 4.3.1. Comparison Service Implementation

#### 4.3.2. Feedback Generation

#### 4.3.3. Constructive Improvement Suggestions

---

## Closing

If you try MetaCheck in your classroom or adapt it for your institution, I would be interested to hear about your experience. If you encounter issues or have suggestions for educational use cases, feel free to share them in the comments.

---

**GitHub Repository:** [MetaCheck - An Evidence-Based Fact Checker](https://github.com/umairalipathan1980/MetaCheck---An-Evidence-Based-Fact-Checker)
