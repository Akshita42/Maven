# ─────────────────────────────────────────────────────────────────
# src/committee/registry.py
# ─────────────────────────────────────────────────────────────────
#
# Dynamic Reviewer Registry for registering and loading committee members.
# ─────────────────────────────────────────────────────────────────

from typing import List, Dict
from src.committee.interfaces import BaseReviewer

class ReviewerRegistry:
    """
    Registry for managing registered BaseReviewer instances.
    Ensures unique reviewerId mapping and preserves insertion order.
    """
    _registry: Dict[str, BaseReviewer] = {}

    @classmethod
    def register(cls, reviewer: BaseReviewer) -> None:
        """
        Registers a reviewer instance. Raises ValueError if reviewerId is duplicate.
        """
        r_id = reviewer.reviewerId
        if not r_id:
            raise ValueError("Reviewer must expose a non-empty reviewerId.")
        if r_id in cls._registry:
            raise ValueError(f"Duplicate reviewer registration error: ID '{r_id}' already registered.")
        cls._registry[r_id] = reviewer

    @classmethod
    def get_reviewers(cls) -> List[BaseReviewer]:
        """
        Returns a list of all registered reviewers in their insertion order.
        """
        return list(cls._registry.values())

    @classmethod
    def clear(cls) -> None:
        """
        Clears all registered reviewers. Useful for test isolation.
        """
        cls._registry.clear()
