# ─────────────────────────────────────────────────────────────────
# src/intelligence/interfaces.py
# ─────────────────────────────────────────────────────────────────
#
# Abstract base interfaces for Analyzers and LLM boundaries.
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
from typing import List
from src.intelligence.models import PillarResult, ReasoningContext, DecisionTrace

class BaseAnalyzer(ABC):
    """
    Standard interface that every Investment Intelligence Analyzer must implement.
    Ensures unified parameter input and deterministic returns.
    """
    @abstractmethod
    def analyze(self, context: ReasoningContext) -> PillarResult:
        """
        Performs analysis on the reasoning context.
        Must be side-effect free and completely deterministic.
        """
        pass

class LLMService(ABC):
    """
    Abstract interface for natural language synthesis, critique, and explanations.
    Keeps the Intelligence Layer provider-independent.
    """
    @abstractmethod
    def summarize(self, ticker: str, pillars: List[PillarResult]) -> str:
        """Generates a structured executive summary synthesis."""
        pass

    @abstractmethod
    def critique(self, ticker: str, pillars: List[PillarResult]) -> str:
        """Provides an adversarial critique of the investment findings."""
        pass

    @abstractmethod
    def generate_explanation(self, pillar: str, traces: List[DecisionTrace]) -> str:
        """Generates natural language reasoning from trace logs."""
        pass
