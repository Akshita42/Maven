# ─────────────────────────────────────────────────────────────────
# src/committee/interfaces.py
# ─────────────────────────────────────────────────────────────────
#
# Abstract interfaces for deterministic investment committee reviewers.
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
from typing import Optional
from src.committee.constants import ReviewerType
from src.thesis.models import InvestmentThesis
from src.committee.models import CommitteeOpinion

class BaseReviewer(ABC):
    """
    Abstract Base Class for all Investment Committee reviewers.
    Each reviewer must be stateless and return an immutable CommitteeOpinion.
    """
    @property
    @abstractmethod
    def reviewerId(self) -> str:
        """The stable unique string identifier for the reviewer."""
        pass

    @property
    @abstractmethod
    def reviewerType(self) -> Optional[ReviewerType]:
        """Optional production reviewer type enum for built-in reviewers."""
        pass

    @property
    @abstractmethod
    def reviewerVersion(self) -> str:
        """Version string of the reviewer code package."""
        pass

    @property
    @abstractmethod
    def rulesVersion(self) -> str:
        """Version string of the rules evaluated by the reviewer."""
        pass

    @abstractmethod
    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        """Evaluates the investment thesis and returns a structured opinion."""
        pass
