"""
Comparison Analysis Service

Service for analyzing student claims versus AI-extracted claims.
"""

import json
import os
from openai import AsyncOpenAI

from app.core.models import ComparisonAnalysis
from app.core.constants import MODEL_NAME


async def run_comparison_analysis(student_claims: list, ai_result) -> ComparisonAnalysis:
    """
    Run comparison analysis between student claims and AI results.

    Args:
        student_claims: List of student claim dictionaries
        ai_result: FinalAssessment from AI verification

    Returns:
        ComparisonAnalysis with feedback and insights
    """
    # Format student claims for the agent
    student_data = []
    for i, claim in enumerate(student_claims):
        student_data.append({
            "index": i + 1,
            "claim": claim.claim if hasattr(claim, 'claim') else claim.get('claim'),
            "verdict": claim.verdict if hasattr(claim, 'verdict') else claim.get('verdict'),
            "confidence": claim.confidence if hasattr(claim, 'confidence') else claim.get('confidence'),
            "reasoning": claim.reasoning if hasattr(claim, 'reasoning') else claim.get('reasoning'),
            "sources_count": claim.sourcesCount if hasattr(claim, 'sourcesCount') else claim.get('sourcesCount'),
            "time_spent": claim.timeSpent if hasattr(claim, 'timeSpent') else claim.get('timeSpent'),
            "key_sources": claim.keySources if hasattr(claim, 'keySources') else claim.get('keySources', []),
        })

    # Format AI claims for the agent
    ai_data = []
    ai_claims = ai_result.claim_results if hasattr(ai_result, 'claim_results') else ai_result.get('claim_results', [])
    for i, claim in enumerate(ai_claims):
        ai_data.append({
            "index": i + 1,
            "claim": claim.claim if hasattr(claim, 'claim') else claim.get('claim'),
            "verdict": claim.verdict if hasattr(claim, 'verdict') else claim.get('verdict'),
            "confidence": claim.confidence if hasattr(claim, 'confidence') else claim.get('confidence'),
            "justification": claim.justification if hasattr(claim, 'justification') else claim.get('justification'),
            "key_sources": claim.key_sources if hasattr(claim, 'key_sources') else claim.get('key_sources', []),
            "sources_count": len(claim.key_sources) if hasattr(claim, 'key_sources') else len(claim.get('key_sources', [])),
        })

    # Build prompt for direct LLM call
    system_prompt = """You are an educational feedback specialist analyzing how a student's fact-checking compares to AI analysis.

Analyze the student's claims and verdicts against the AI's extracted claims and verdicts, providing CONCISE educational feedback.

Provide ONLY these two sections:

1. **overall_summary** 
   - Brief high-level assessment of the student's performance
   - Note overall agreement/disagreement patterns
   - Keep it simple and encouraging

2. **areas_for_improvement** (or empty array if performance was strong)
   - Specific, actionable suggestions
   - Focus on the most important improvements only
   - Leave empty if student work was already strong

Do NOT populate: strengths, key_insights, claim_by_claim_feedback, learning_opportunities, or encouragement fields.

Keep all feedback brief, student-friendly, and focused on actionable insights."""

    user_prompt = f"""Analyze the following comparison between student claims and AI-extracted claims:

**STUDENT CLAIMS ({len(student_data)} total):**
{json.dumps(student_data, indent=2)}

**AI-EXTRACTED CLAIMS ({len(ai_data)} total):**
{json.dumps(ai_data, indent=2)}

Provide your analysis following the format specified."""

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback if API key missing
        return ComparisonAnalysis(
            overall_summary="Unable to generate comparison analysis: API key not configured.",
            strengths=[],
            areas_for_improvement=["Please configure OPENAI_API_KEY environment variable."],
            key_insights=[],
            claim_by_claim_feedback=[],
            learning_opportunities=[],
            encouragement=""
        )

    client = AsyncOpenAI(api_key=api_key)

    try:
        # Prepare API call parameters
        api_params = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": ComparisonAnalysis,
            "temperature": 0.3,
        }

        # Use correct token parameter based on model family
        if MODEL_NAME.startswith("gpt-5"):
            api_params["max_completion_tokens"] = 2048
        else:
            api_params["max_tokens"] = 2048

        # Make direct API call with structured output
        response = await client.beta.chat.completions.parse(**api_params)

        # Extract the parsed response
        if response.choices and response.choices[0].message.parsed:
            return response.choices[0].message.parsed

        # Fallback if parsing fails
        return ComparisonAnalysis(
            overall_summary="Unable to parse comparison analysis response.",
            strengths=[],
            areas_for_improvement=["Please try again."],
            key_insights=[],
            claim_by_claim_feedback=[],
            learning_opportunities=[],
            encouragement=""
        )

    except Exception as exc:
        # Fallback on any error
        return ComparisonAnalysis(
            overall_summary=f"Unable to generate comparison analysis: {str(exc)}",
            strengths=[],
            areas_for_improvement=["Please try again later."],
            key_insights=[],
            claim_by_claim_feedback=[],
            learning_opportunities=[],
            encouragement=""
        )
