# ─────────────────────────────────────────────────────────────────
# src/critique/interfaces.py
# ─────────────────────────────────────────────────────────────────
#
# Abstract interfaces for mockable infrastructure boundary services.
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """
    Abstract interface for LLM operations.
    Keeps the AI Engine completely independent of concrete providers.
    """
    @abstractmethod
    def generate_json_response(self, system_prompt: str, user_prompt: str, timeout: float = 10.0) -> str:
        """
        Sends requests to the configured LLM and returns a raw text JSON response.
        Enforces a strict timeout bounds parameter.
        """
        pass
