"""
MetaCheck Core Package

Public API:
    - verify_claims: Main fact-checking workflow
    - FinalAssessment: Result model
"""

from app.core.workflow import verify_claims
from app.core.models import FinalAssessment

__all__ = ["verify_claims", "FinalAssessment"]
