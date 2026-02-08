"""
MetaCheck Analysis Classes

Metacognitive tracking for the fact-checking workflow.
"""

from datetime import datetime
from typing import List, Optional

from app.core.models import (
    Evidence,
    MetacognitiveStep,
    ContradictionDetection,
)


# ============================================================================
# METACOGNITIVE TRACKER
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
