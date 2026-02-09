# MetaCheck Documentation

**Complete guide to using MetaCheck for educational fact-checking and media literacy learning**

---

## Table of Contents

1. [How to Use](#1-how-to-use)
2. [How It Works](#2-how-it-works)
3. [Understanding Verdicts](#3-understanding-verdicts)
4. [Evidence Sources](#4-evidence-sources)
5. [Educational Use](#5-educational-use)

---

## 1. How to Use

### Overview

MetaCheck is an educational tool that helps students learn fact-checking by comparing their own assessment with AI-generated analysis. The workflow consists of three main steps:

1. **Your Assessment** - Do your own fact-checking first
2. **AI Analysis** - Let AI verify the same claims
3. **Compare** - See how your assessment compares with AI

### Step 1: Your Assessment

**Why start with your assessment?**

By doing your own fact-checking first, you develop critical thinking skills before seeing the AI's approach. This pedagogical design prevents "answer-seeking" behavior and encourages genuine learning.

**How to create your assessment:**

1. **Add Claims Manually**
   - Click "+ Add New Claim" button
   - Enter the claim text you want to verify
   - Research the claim using multiple sources
   - Gather evidence and assess credibility

2. **Determine Your Verdict**
   - Choose from: SUPPORTED, REFUTED, INSUFFICIENT_INFORMATION, or CONFLICTING_EVIDENCE
   - Set your confidence level (0.0 to 1.0)
   - Record how many sources you consulted
   - Track time spent on verification

3. **Write Your Reasoning**
   - Explain why you reached your verdict
   - Cite specific sources and evidence
   - Note any assumptions or uncertainties

**Guidelines for Assessment:**

Refer to the collapsible "How to Assess Claims (Guidelines)" section in the Your Assessment tab, which includes:

- **Extract Verifiable Claims**: Identify statements that can be proven true or false
- **Collect Evidence from Multiple Sources**: Use search engines, Wikipedia, fact-checking sites, primary sources
- **Evaluate Source Credibility**: Consider authority, bias, evidence quality, timeliness
- **Choose a Verdict**: Based on the evidence strength
- **Set Confidence Level**: How certain are you about your verdict?
- **Write Your Reasoning**: Explain your critical thinking process

### Step 2: AI Analysis

**Automated Verification:**

After completing your assessment, you can run AI verification on the same text:

1. **Input Text**: Paste or type the text containing claims
2. **Extract Claims**: AI automatically identifies verifiable claims
3. **Select Claims**: Choose which claims to verify (up to 5)
4. **Run Verification**: AI searches multiple sources and generates verdicts

**What AI Does:**

- Searches 3 evidence sources in parallel (Web, Wikipedia, Fact Check databases)
- Assigns credibility scores to each source
- Analyzes stance (supports/refutes/neutral)
- Synthesizes a verdict with confidence and justification
- Provides full transparency through metacognitive detail (Comprehensive mode)

**Basic vs. Comprehensive Mode:**

- **Basic**: Faster, concise justifications (1-2 sentences)
- **Comprehensive**: Detailed reasoning, full metacognitive transparency, more sources

### Step 3: Compare & Learn

**Educational Comparison:**

After both assessments are complete:

1. View side-by-side comparison of your verdict vs. AI verdict
2. See overall summary of your performance
3. Review areas for improvement (if any)
4. Learn professional fact-checking techniques

**What You'll Learn:**

- How professional fact-checkers approach claims
- Source selection strategies
- Evidence synthesis techniques
- Confidence calibration
- Reasoning transparency

---

## 2. How It Works

### MetaCheck Workflow

**Educational Workflow:**

1. **Your Assessment** → Extract claims, gather evidence, make your own verdict
2. **AI Verification** → AI agents search sources, analyze evidence, generate verdicts
3. **Compare & Learn** → See how your assessment compares with AI and get feedback

**Educational Insight:** By doing your own fact-checking first, you develop critical thinking skills before seeing the AI's approach. The comparison helps you learn professional fact-checking techniques.

### How MetaCheck Works Behind the Scenes

Understanding the technical workflow helps you interpret results and troubleshoot issues. MetaCheck uses an **agentic AI architecture** with specialized components working together.

#### Complete Technical Workflow

**Step 1: INPUT**
- User provides text to verify

**Step 2: CLAIM EXTRACTION**
- AI extracts verifiable claims (Claim Extractor Agent)

**Step 3: USER SELECTION**
- User selects claims to verify

**Step 4: PARALLEL VERIFICATION AGENTS**
- System spawns one agent per selected claim (all run simultaneously)
- Each agent performs:
  - **Parallel Search**: Web 🌐, Wikipedia 📚, Fact Check ✓
  - **Process Evidence**: Credibility scoring + Stance analysis
  - **Verdict**: With Confidence + Justification

**Step 5: AGGREGATION**
- Collect all verdicts + evidence

**Step 6: FINAL ASSESSMENT**
- Complete analysis with sources

**Technical Implementation:** Uses OpenAI Agents SDK with parallel tool execution. Each verification agent is an autonomous AI that orchestrates evidence gathering, analyzes credibility, determines stance, and synthesizes a verdict with full reasoning transparency.

### The Verification Pipeline

#### Phase 1: Claim Extraction

**Component:** Claim Extractor Agent

**What happens:** The AI analyzes your input text and identifies statements that are:
- Specific and concrete (not vague)
- Falsifiable (can be proven true or false)
- Require external verification (not common knowledge)
- Contain verifiable details (numbers, dates, names, locations)

**Output:** A list of candidate claims extracted from your text

#### Phase 2: Claim Selection

**Component:** User Interface (Manual Selection)

**What happens:** You review the extracted claims and select which ones you want to verify. This gives you control over what gets fact-checked and helps manage processing time and cost.

#### Phase 3: Parallel Evidence Gathering

**Component:** Orchestrator Agent with comprehensive_evidence_tool

**What happens:** For each selected claim, the system simultaneously searches three sources:

1. **Tavily Web Search**: Finds relevant web pages and snippets
2. **Wikipedia**: Searches encyclopedic articles
3. **Google Fact Check API**: Queries professional fact-checking databases

All three searches run **in parallel** (simultaneously), significantly reducing processing time.

**Output:** Combined evidence bundle with snippets, URLs, source types, and preliminary scores

#### Phase 4: Credibility Classification

**Component:** Domain Classification (config-based lookup)

**What happens:** Each web search result is analyzed to determine its credibility:
- Domain is extracted from the URL
- Domain is matched against a taxonomy (government, academic, news, etc.)
- Credibility score is assigned based on category (0.50-0.90)

**Note:** Wikipedia (0.80) and Fact Check (0.95) have fixed scores. Only web search results use dynamic domain classification.

#### Phase 5: Stance Analysis

**Component:** Orchestrator Agent (AI Analysis)

**What happens:** The AI reads each evidence snippet and determines its stance:
- **Supports**: Evidence confirms or aligns with the claim
- **Refutes**: Evidence contradicts or disproves the claim
- **Neutral**: Evidence is related but doesn't clearly support or refute
- **Unclear**: Evidence is ambiguous or indirect

For Fact Check sources, the stance is automatically interpreted from ratings. For web and Wikipedia, the AI analyzes the snippet text.

#### Phase 6: Verdict Synthesis

**Component:** Orchestrator Agent (Decision Logic)

**What happens:** The AI synthesizes all evidence and reaches a verdict:

1. Calculate total credibility weight for supporting evidence
2. Calculate total credibility weight for refuting evidence
3. Apply verdict criteria based on weights and thresholds
4. Determine confidence score based on evidence quality and quantity
5. Generate justification explaining the verdict
6. (Comprehensive mode only) Document metacognitive detail with full reasoning transparency

**Output:** VerificationResult with verdict, confidence, justification, sources, and evidence list

### Mode Differences Explained

| Aspect | Basic Mode | Comprehensive Mode |
|--------|-----------|-------------------|
| **Primary Use Case** | Quick fact-checking, classroom demos, fast results | Deep learning, understanding reasoning, educational transparency |
| **Evidence Retrieved** | Limited (3 web, 2 wiki, 2 fact-check) | More comprehensive (5 web, 3 wiki, 3 fact-check) |
| **Justification** | 1-2 concise sentences explaining verdict | Detailed paragraph with reasoning and evidence summary |
| **Metacognitive Detail** | Not included (empty) | Full transparency: search queries, source assessments, verdict reasoning, AI uncertainties, assumptions |
| **Processing Time** | Faster (~10-20 seconds per claim) | Slower (~15-30 seconds per claim) |
| **Max Claims** | 5 claims | 5 claims |
| **Best For** | Quick demos, time-constrained situations | Educational deep dives, learning AI reasoning, research |
| **API Cost** | Lower (fewer API calls) | Higher (more comprehensive analysis) |

### Parallelism Architecture

MetaCheck uses **two levels of parallelism** for optimal performance:

1. **Agent-Level Parallelism**: All selected claims are verified simultaneously (not sequentially)
2. **Tool-Level Parallelism**: Within each agent, all 3 evidence sources are searched in parallel

This architecture significantly reduces total verification time.

---

## 3. Understanding Verdicts

### Verdict Categories

MetaCheck uses four verdict categories based on evidence strength and consistency:

#### ✅ SUPPORTED

**Meaning:** The claim is backed by credible evidence from multiple sources.

**Criteria:**
- Supporting evidence significantly outweighs refuting evidence
- High credibility sources confirm the claim
- Consensus across multiple independent sources
- No significant contradictions from reliable sources

**Example:** "The Eiffel Tower is 330 meters tall" → Multiple authoritative sources (Wikipedia, official websites, encyclopedias) confirm this measurement.

**Confidence Interpretation:**
- 0.8-1.0: Very strong support from many high-quality sources
- 0.6-0.7: Moderate support, some gaps or lower-quality sources
- 0.5: Borderline, minimal support

#### ❌ REFUTED

**Meaning:** The claim is contradicted by credible evidence.

**Criteria:**
- Refuting evidence significantly outweighs supporting evidence
- High credibility sources contradict the claim
- Fact-checkers have rated it false or misleading
- Evidence demonstrates the opposite is true

**Example:** "Vaccines cause autism" → Multiple scientific studies, medical organizations, and fact-checkers have thoroughly debunked this claim.

**Confidence Interpretation:**
- 0.8-1.0: Very strong refutation from authoritative sources
- 0.6-0.7: Clear contradiction but from fewer sources
- 0.5: Borderline, weak refutation

#### ⚠️ CONFLICTING_EVIDENCE

**Meaning:** Different credible sources provide contradictory information.

**Criteria:**
- Both supporting and refuting evidence exist in significant amounts
- Credible sources disagree with each other
- No clear consensus in the evidence
- The truth may depend on context, interpretation, or ongoing debate

**Example:** "Remote work increases productivity" → Some studies show productivity gains, others show productivity losses. The truth varies by industry, role, and measurement methodology.

**When to use:**
- Genuine scientific or expert disagreement
- Politically polarized topics with partisan sources
- Evolving situations where facts are still being established
- Complex claims where "it depends" is the honest answer

#### ❓ INSUFFICIENT_INFORMATION

**Meaning:** Not enough reliable evidence was found to make a determination.

**Criteria:**
- Very few sources found (or sources have low credibility scores)
- Total credibility weight below minimum threshold (typically < 0.7)
- Evidence is tangential or doesn't directly address the claim
- Sources are unreliable, outdated, or irrelevant

**Example:** "John Smith's bakery in Springfield has the best croissants" → Too specific/local to have authoritative sources. Subjective claim without verifiable evidence.

**Common Causes:**
- Very new events (not yet in databases)
- Hyper-local claims (small town events, local businesses)
- Obscure historical facts
- Claims about non-public figures
- Subjective statements ("best", "most beautiful")

### Confidence Scores

**What is confidence?**

A numerical score (0.0 to 1.0) indicating how certain the AI is about its verdict.

**How it's calculated:**

Confidence is based on:
- **Evidence quantity**: More sources = higher confidence
- **Evidence quality**: Higher credibility sources = higher confidence
- **Evidence consistency**: Agreement among sources = higher confidence
- **Search success**: Successful searches = higher confidence

**Interpretation:**

- **0.9-1.0**: Extremely confident (strong, consistent evidence from many high-quality sources)
- **0.7-0.8**: Confident (solid evidence from reliable sources)
- **0.5-0.6**: Moderate confidence (some evidence, but gaps or inconsistencies)
- **0.3-0.4**: Low confidence (weak evidence, few sources, low quality)
- **0.0-0.2**: Very low confidence (almost no evidence, unreliable sources)

**Important Notes:**

- High confidence does NOT guarantee the verdict is correct (AI can be confidently wrong)
- Low confidence often indicates insufficient evidence, not necessarily that the claim is false
- Confidence reflects evidence strength, not absolute truth

### Justification

**What is justification?**

A human-readable explanation of why the AI reached its verdict. This is the "reasoning" section that explains the evidence and decision process.

**Basic Mode Justification:**
- 1-2 concise sentences
- Summarizes the key evidence
- States the verdict and primary reason

**Comprehensive Mode Justification:**
- Detailed paragraph
- Explains evidence from each source
- Discusses evidence weight and credibility
- Addresses contradictions or uncertainties
- Transparent about reasoning process

### Metacognitive Detail (Comprehensive Mode Only)

**What is metacognitive detail?**

A detailed breakdown of the AI's reasoning process, showing "thinking out loud" transparency.

**What's included:**

1. **Search Queries Used**: Exact queries sent to each evidence source
2. **Source Assessments**: How each source was evaluated for credibility and stance
3. **Evidence Synthesis**: How different pieces of evidence were combined
4. **Verdict Reasoning**: The logical steps that led to the final verdict
5. **Uncertainties & Assumptions**: What the AI is unsure about or had to assume
6. **Alternative Interpretations**: Other ways the evidence could be interpreted

**Why is it useful?**

- **Educational**: Students learn how professional fact-checkers think
- **Transparency**: Users can audit the AI's reasoning
- **Debugging**: Helps identify when AI misunderstood something
- **Trust**: Users can verify the reasoning makes sense

### Evidence Sources

Each verdict includes a list of evidence sources with:

- **URL**: Link to the source
- **Title**: Title or snippet from the source
- **Source Type**: web, wikipedia, or factcheck
- **Credibility Score**: 0.0-1.0 (higher = more trustworthy)
- **Stance**: supports, refutes, neutral, or unclear
- **Domain Category**: government, academic, news, etc. (for web sources)

### Search Status

Each evidence source also has a search status:

- **success**: Search ran successfully and found results
- **no_results**: Search completed but found no matching evidence
- **error**: Search failed due to API error or network issue
- **no_api_key**: API key not configured for this source type

### Common Verdict Patterns

**Pattern 1: Strong Consensus**
- Verdict: SUPPORTED or REFUTED
- Confidence: 0.8-1.0
- All sources agree
- High credibility sources

**Pattern 2: Weak Evidence**
- Verdict: INSUFFICIENT_INFORMATION
- Confidence: 0.3-0.5
- Few sources found
- Low credibility scores

**Pattern 3: Genuine Disagreement**
- Verdict: CONFLICTING_EVIDENCE
- Confidence: 0.5-0.7
- Credible sources on both sides
- No clear consensus

**Pattern 4: Search Failures**
- Verdict: INSUFFICIENT_INFORMATION
- Confidence: 0.0-0.3
- Multiple search errors
- No usable evidence retrieved

---

## 4. Evidence Sources

### Overview of Evidence Sources

MetaCheck searches three types of evidence sources for each claim:

1. **Web Search (Tavily)**
2. **Wikipedia**
3. **Google Fact Check API**

All three sources are queried **in parallel** (simultaneously) to maximize speed.

### 1. Web Search (Tavily)

**What is Tavily?**

Tavily is a search API optimized for AI agents and LLM applications. It provides relevant, high-quality web search results with clean snippets.

**How MetaCheck uses it:**

- Searches the open web for claim-related content
- Returns relevant snippets and URLs
- Prioritizes authoritative sources
- Filters out low-quality content

**Search Depth:**

- **Basic**: Quick search, fewer results
- **Advanced**: More thorough search, more results (configurable in Settings)

**Credibility Scoring:**

Web search results are scored based on **domain classification**:

| Domain Category | Credibility Score | Examples |
|----------------|-------------------|----------|
| **Government** | 0.90 | .gov, .mil, official government sites |
| **Academic** | 0.85 | .edu, university sites, research institutions |
| **Medical/Health Authority** | 0.85 | WHO, CDC, NIH, medical journals |
| **Fact-Checking Organizations** | 0.85 | Snopes, FactCheck.org, PolitiFact |
| **Major News (High Reputation)** | 0.75 | AP, Reuters, BBC, NYT, WSJ |
| **Major News (Mainstream)** | 0.70 | CNN, Fox News, Guardian, etc. |
| **Non-Profit Organizations** | 0.70 | .org domains, NGOs |
| **General News/Media** | 0.60 | Regional news, smaller outlets |
| **Commercial/Business** | 0.55 | .com domains, corporate sites |
| **Unknown/Uncategorized** | 0.50 | Domains not in taxonomy |

**Limitations:**

- May miss paywalled content
- Cannot access private databases
- Subject to search API coverage
- Domain classification may not capture all nuances

### 2. Wikipedia

**What is Wikipedia?**

Wikipedia is a free online encyclopedia with millions of articles. While not peer-reviewed, it's generally reliable for factual information and provides good starting points for research.

**How MetaCheck uses it:**

- Searches Wikipedia articles for claim-related content
- Extracts relevant paragraphs
- Provides context and background information
- Links to original articles for verification

**Credibility Score:** Fixed at **0.80**

**Why 0.80?**
- Wikipedia is generally accurate for mainstream topics
- Articles are collaboratively edited and monitored
- Citations provide traceability to original sources
- Not peer-reviewed, so not as authoritative as academic sources

**Strengths:**
- Comprehensive coverage of many topics
- Well-structured, neutral point of view
- Frequently updated
- Good for historical facts, definitions, basic information

**Limitations:**
- Can be vandalized (though usually quickly corrected)
- Not appropriate for highly specialized topics
- May lag behind very recent events
- Not suitable as a primary source for academic research

### 3. Google Fact Check API

**What is Google Fact Check API?**

The Google Fact Check Tools API searches a database of fact-checks from professional fact-checking organizations worldwide.

**How MetaCheck uses it:**

- Queries the fact-check database for matching claims
- Returns fact-checks from organizations like Snopes, FactCheck.org, PolitiFact
- Includes the fact-checker's verdict (e.g., "True", "False", "Mostly False")
- Provides claim context and reasoning

**Credibility Score:** Fixed at **0.95**

**Why 0.95?**
- Professional fact-checkers are experts in verification
- Rigorous editorial standards
- Transparent methodology
- Explicitly designed for claim verification

**Strengths:**
- Highest credibility of all sources
- Expert analysis with detailed reasoning
- Covers popular claims and misinformation
- Includes context and explanation

**Limitations:**
- Coverage is limited to claims that fact-checkers have investigated
- Typically focuses on viral misinformation and public statements
- May not cover obscure or local claims
- No results ≠ claim is false (just means not fact-checked yet)

### Source Comparison

| Aspect | Web Search (Tavily) | Wikipedia | Fact Check API |
|--------|-------------------|-----------|----------------|
| **Credibility** | 0.50-0.90 (varies) | 0.80 (fixed) | 0.95 (fixed) |
| **Coverage** | Broad (entire web) | Encyclopedic topics | Fact-checked claims only |
| **Freshness** | Very current | Usually current | Depends on fact-checkers |
| **Depth** | Varies widely | Medium depth | Deep analysis |
| **Expertise** | Varies by source | Collaborative | Professional fact-checkers |
| **Best For** | Current events, diverse perspectives | Background, definitions, history | Debunked claims, misinformation |

### Evidence Synthesis

**How MetaCheck combines evidence:**

1. **Collect** all evidence from all three sources
2. **Score credibility** based on source type and domain
3. **Determine stance** (supports/refutes/neutral) for each piece of evidence
4. **Calculate weighted evidence** (credibility × stance)
5. **Synthesize verdict** based on total evidence weight
6. **Generate confidence** based on quantity, quality, and consistency

### Search Status Indicators

Each source search has a status:

| Status | Meaning | Implication | Action |
|--------|---------|-------------|--------|
| **success** | Search ran successfully and found results | Evidence is usable | None — working as expected |
| **no_results** | Search ran but found no matching evidence | This is an absence of evidence, not a system error | None — this is normal for many claims |
| **error** | Search failed due to API error, network issue | Evidence may be incomplete. Verdict is based only on sources that succeeded | Try again later or check system status |
| **no_api_key** | API key for this source was not configured | That source type was disabled for this run. Verdict is based on remaining sources | System administrator needs to configure API key |

### Quality Assurance

**How to assess evidence quality:**

1. **Check credibility scores**: Higher is better (> 0.7 is generally reliable)
2. **Verify source diversity**: Multiple independent sources are better than one
3. **Review search status**: Ensure searches succeeded
4. **Read justification**: Understand how AI interpreted the evidence
5. **Follow links**: Verify AI interpretation by reading original sources
6. **Check for bias**: Consider potential biases in source selection

---

## 5. Educational Use

### Learning Objectives

MetaCheck is designed to help students develop:

1. **Critical Thinking**: Evaluate claims independently before seeking answers
2. **Media Literacy**: Understand how to assess source credibility
3. **Research Skills**: Learn effective search strategies and source evaluation
4. **Metacognition**: Reflect on their own reasoning process
5. **AI Literacy**: Understand how AI makes decisions and where it can fail

### Pedagogical Approach

**Compare-and-Contrast Learning:**

MetaCheck uses a "Do-it-yourself first, then compare" pedagogy:

1. **Student completes task independently** (no AI guidance)
2. **AI completes the same task** (transparent reasoning)
3. **Student compares** their approach with AI's approach
4. **Student reflects** on differences and learns from comparison

**Why this works:**

- **Prevents answer-seeking**: Students must think first
- **Encourages genuine effort**: No way to "cheat" by copying AI
- **Promotes metacognition**: Students see their own thinking vs. expert thinking
- **Builds confidence**: Students see what they got right
- **Identifies gaps**: Students see where they can improve

### Classroom Use Cases

#### Use Case 1: Fact-Checking Exercise

**Objective:** Teach students how to verify claims using multiple sources

**Activity:**
1. Provide a text with several factual claims (news article, social media post)
2. Students manually fact-check using search engines and databases
3. Students record their findings in MetaCheck
4. Run AI verification on the same text
5. Compare results and discuss differences in class

**Discussion Points:**
- Which sources did students miss?
- How did students assess credibility differently than AI?
- What search strategies were most effective?

#### Use Case 2: Misinformation Detection

**Objective:** Help students identify and debunk common misinformation

**Activity:**
1. Present a viral claim or conspiracy theory
2. Students research and create their own assessment
3. AI verifies the same claim
4. Compare verdicts and review fact-checker sources
5. Discuss why misinformation spreads despite evidence

**Discussion Points:**
- What makes a source credible?
- Why do people believe false claims?
- How can we communicate corrections effectively?

#### Use Case 3: Source Credibility Training

**Objective:** Teach students to evaluate source reliability

**Activity:**
1. Students assess a claim with diverse sources (academic, news, blogs, social media)
2. Students assign their own credibility scores to each source
3. Compare with MetaCheck's domain classification system
4. Discuss agreements and disagreements

**Discussion Points:**
- What makes a source credible?
- How should domain (.gov, .edu, .com) influence trust?
- When might a "lower credibility" source still be valuable?

#### Use Case 4: AI Transparency & Limitations

**Objective:** Help students understand how AI works and where it can fail

**Activity:**
1. Give students a tricky claim (ambiguous, context-dependent, or nuanced)
2. Students predict how AI will handle it
3. Run verification in Comprehensive mode
4. Analyze metacognitive detail
5. Identify where AI succeeded and where it struggled

**Discussion Points:**
- What can AI do well vs. poorly?
- How can we audit AI reasoning?
- When should we trust AI vs. human judgment?

### Assessment Rubrics

**Suggested Grading Criteria for Student Assessments:**

| Criterion | Poor (0-2) | Satisfactory (3-4) | Excellent (5) |
|-----------|-----------|-------------------|---------------|
| **Evidence Quality** | Used 0-1 sources, unreliable sources | Used 2-3 sources, mostly credible | Used 3+ diverse, highly credible sources |
| **Source Evaluation** | Did not assess credibility | Basic credibility assessment | Thorough credibility analysis with reasoning |
| **Reasoning** | Vague or missing justification | Clear reasoning with some evidence | Detailed, logical reasoning citing specific evidence |
| **Verdict Accuracy** | Incorrect verdict based on evidence | Reasonable verdict but could be stronger | Well-supported verdict matching evidence |
| **Confidence Calibration** | Confidence wildly misaligned with evidence | Confidence somewhat aligned | Confidence well-calibrated to evidence strength |

### Tips for Instructors

**Before using MetaCheck:**

1. **Set expectations**: Explain the "do-it-yourself first" approach
2. **Model the process**: Demonstrate a complete assessment as an example
3. **Provide guidelines**: Share the assessment guidelines from the tool
4. **Discuss credibility**: Review the credibility scoring system
5. **Practice**: Start with simple, unambiguous claims

**During the activity:**

1. **Encourage thoroughness**: Remind students to use multiple sources
2. **Require documentation**: Students should record sources and reasoning
3. **Allow adequate time**: Fact-checking takes time (15-30 min per claim)
4. **Discourage guessing**: Better to say "insufficient information" than guess
5. **Monitor progress**: Check that students are engaging meaningfully

**After comparison:**

1. **Facilitate reflection**: Have students write about what they learned
2. **Discuss patterns**: Identify common mistakes or successes
3. **Address surprises**: Talk about unexpected differences
4. **Highlight strengths**: Celebrate what students did well
5. **Identify improvements**: Discuss specific areas for growth

### Advanced Features for Educators

**Settings Configuration (Admin Only):**

Instructors can adjust:
- Number of claims to verify per run
- Number of sources to search
- Model choice (faster vs. more accurate)
- Search depth (basic vs. advanced)
- Timeout settings

**Comparison Feedback:**

The comparison tab provides:
- Overall summary of student performance
- Areas for improvement (specific, actionable feedback)
- Recognition of what was done well

**Export Functionality:**

Students and instructors can export:
- Complete assessment as JSON
- Full verification results
- Comparison analysis

### Best Practices

**For Students:**

1. **Take your time**: Thorough fact-checking requires patience
2. **Use multiple sources**: Don't rely on just one website
3. **Check credibility**: Look for author credentials, publication date, domain
4. **Be honest about confidence**: It's okay to be uncertain
5. **Cite specific evidence**: Don't just say "I googled it"
6. **Document your process**: Track sources, time, reasoning

**For Instructors:**

1. **Start simple**: Use clear, unambiguous claims first
2. **Scaffold the process**: Provide templates or worksheets initially
3. **Make it collaborative**: Have students work in pairs or small groups
4. **Connect to current events**: Use recent news or viral claims
5. **Emphasize learning over grades**: Focus on improvement, not perfection
6. **Model transparency**: Share your own fact-checking process

### Common Challenges & Solutions

**Challenge 1: Students rush through assessment**

**Solution:**
- Require minimum number of sources (3-5)
- Have students submit source list before verdict
- Track and require minimum time spent
- Make assessment a significant portion of grade

**Challenge 2: Students copy AI results**

**Solution:**
- Require students to submit assessment BEFORE running AI
- Use timestamp tracking
- Require written reflection on differences
- Focus on process, not just final answer

**Challenge 3: Disagreement with AI verdict**

**Solution:**
- Emphasize that disagreement is okay (AI can be wrong)
- Have students defend their position with evidence
- Discuss nuances and context the AI may have missed
- Use it as a teaching moment about AI limitations

**Challenge 4: Students don't know where to start**

**Solution:**
- Provide assessment guidelines (included in tool)
- Model the process with an example
- Offer search strategy tips
- Start with simpler, more straightforward claims

### Resources for Further Learning

**Fact-Checking Organizations:**
- [FactCheck.org](https://www.factcheck.org/)
- [Snopes](https://www.snopes.com/)
- [PolitiFact](https://www.politifact.com/)
- [Full Fact (UK)](https://fullfact.org/)

**Media Literacy Resources:**
- [News Literacy Project](https://newslit.org/)
- [Common Sense Media](https://www.commonsensemedia.org/)
- [NAMLE (National Association for Media Literacy Education)](https://namle.net/)

**Source Evaluation Tools:**
- [CRAAP Test](https://library.csuchico.edu/help/source-or-information-good) (Currency, Relevance, Authority, Accuracy, Purpose)
- [SIFT Method](https://www.middlesex.mass.edu/ace/610.htm) (Stop, Investigate source, Find better coverage, Trace claims)
- [Lateral Reading](https://cor.stanford.edu/curriculum/collections/teaching-lateral-reading) (Stanford approach)

---

## Appendix: Technical Specifications

### System Requirements

**Backend:**
- Python 3.12+
- FastAPI framework
- OpenAI Agents SDK
- Tavily API key
- Google Fact Check API key (optional)
- Wikipedia API access token (optional)

**Frontend:**
- Node.js 20+
- React 19+
- Vite build tool
- Tailwind CSS

### API Endpoints

- `POST /api/extract` - Extract claims from text
- `POST /api/verify` - Verify selected claims
- `POST /api/compare` - Compare student vs AI assessment
- `GET /api/config/settings` - Get current settings
- `PUT /api/config/settings` - Update settings (admin only)
- `POST /api/admin/reload-settings` - Reload configuration (admin only)

### Authentication

**Admin access required for:**
- Modifying settings
- Reloading configuration

**Login credentials:**
- Username: `admin`
- Password: Set in `.env` file (`ADMIN_PASSWORD`)

### Configuration

Settings can be adjusted in the Settings tab (admin login required):

- **Max claims to verify per run**: 1-5
- **Max claims to extract**: 1-10
- **Max web search results**: 1-5
- **Max Wikipedia results**: 1-5
- **Max fact-check results**: 1-5
- **Model choice**: gpt-5.1, gpt-4.1-mini, or gpt-5-mini
- **Tavily search depth**: basic or advanced
- **Per-claim timeout**: seconds to wait before timing out

---

## About MetaCheck

**Version:** 1.0.0

**Developer:** Educational AI Research Team

**Purpose:** MetaCheck is designed as an educational tool to help students learn fact-checking, critical thinking, and media literacy skills through hands-on practice and AI-powered comparison.

**License:** Educational use

**Contact:** For questions, issues, or feedback about MetaCheck, please contact your course instructor or system administrator.

---

*This documentation reflects the MetaCheck interface as of the current version. Features and functionality may be updated over time. Always refer to the in-application documentation for the most current information.*
