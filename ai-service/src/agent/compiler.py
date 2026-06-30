# ─────────────────────────────────────────────────────────────────
# src/agent/compiler.py
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Any
from src.domain.contracts.evidence import EvidencePackage

class EvidenceCompiler:
    """
    Acts as a deterministic validation boundary.
    Ensures that semi-structured LLM outputs from the Research Agent
    are rigorously validated and converted into a pristine EvidencePackage
    before entering the Deterministic Pipeline.
    """
    
    @staticmethod
    def compile_evidence(research_result: Dict[str, Any]) -> EvidencePackage:
        """
        Takes raw output from the Research Agent and constructs a Validated EvidencePackage.
        Raises TerminalAgentError if required fields are missing or schema validation fails.
        """
        try:
            # Here, the actual conversion logic would run.
            # For demonstration, we simply pass it to the Pydantic model directly.
            evidence = EvidencePackage(**research_result)
            return evidence
        except Exception as e:
            from src.agent.exceptions import TerminalAgentError
            raise TerminalAgentError(f"Research output failed strict evidence validation: {str(e)}")
