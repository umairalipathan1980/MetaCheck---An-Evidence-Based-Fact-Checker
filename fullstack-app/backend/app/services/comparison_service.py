"""
Comparison Analysis Service

Service for analyzing student claims versus AI-extracted claims.
"""

import json
from agents import Runner

from app.core.agents import comparison_analyzer
from app.core.models import ComparisonAnalysis


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

    # Build prompt for the agent
    prompt = f"""Analyze the following comparison between student claims and AI-extracted claims:

**STUDENT CLAIMS ({len(student_data)} total):**
{json.dumps(student_data, indent=2)}

**AI-EXTRACTED CLAIMS ({len(ai_data)} total):**
{json.dumps(ai_data, indent=2)}

Provide comprehensive educational feedback comparing the student's work with the AI's analysis.
Focus on:
- What the student did well
- Areas for improvement (constructive)
- Key learning insights
- Specific claim-by-claim feedback
- Actionable learning opportunities
- Encouragement

Be supportive, educational, and specific in your feedback."""

    # Run the analyzer agent
    result = await Runner.run(
        comparison_analyzer,
        prompt,
        max_turns=3,
    )

    # Return the structured analysis
    if result and result.final_output:
        return result.final_output

    # Fallback if agent fails
    return ComparisonAnalysis(
        overall_summary="Unable to generate comparison analysis at this time.",
        strengths=["Analysis system encountered an issue."],
        areas_for_improvement=["Please try again later."],
        key_insights=["System feedback unavailable."],
        claim_by_claim_feedback=["Detailed feedback unavailable."],
        learning_opportunities=["Try running the analysis again."],
        encouragement="Keep up the great work with your fact-checking practice!"
    )
