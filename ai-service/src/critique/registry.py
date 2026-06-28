# ─────────────────────────────────────────────────────────────────
# src/critique/registry.py
# ─────────────────────────────────────────────────────────────────
#
# Critique Registry for registering deterministic evaluators.
# ─────────────────────────────────────────────────────────────────

from typing import List

class CritiqueRegistry:
    """
    Registry for dynamic loading of critique evaluators.
    """
    _evaluators: List[str] = []

    @classmethod
    def register_evaluator(cls, name: str) -> None:
        if name not in cls._evaluators:
            cls._evaluators.append(name)

    @classmethod
    def get_evaluators(cls) -> List[str]:
        return list(cls._evaluators)

    @classmethod
    def clear(cls) -> None:
        cls._evaluators.clear()

# Register core default critique evaluators
CritiqueRegistry.register_evaluator("SolvencyStressTest")
CritiqueRegistry.register_evaluator("CoverageAudit")
CritiqueRegistry.register_evaluator("ContradictionCheck")
CritiqueRegistry.register_evaluator("SensitivitySimulation")
