# ─────────────────────────────────────────────────────────────────
# src/infrastructure/llm/factory.py
# ─────────────────────────────────────────────────────────────────

from src.critique.interfaces import BaseLLMService
from src.infrastructure.llm.gemini_service import GeminiService

class LLMFactory:
    """
    Dependency Injection factory for LLM Services.
    Returns the configured LLM provider without coupling the domain.
    """
    
    @staticmethod
    def get_llm_service() -> BaseLLMService:
        # In the future, this could read an env var (e.g. LLM_PROVIDER=gemini)
        # and return different implementations.
        return GeminiService()
