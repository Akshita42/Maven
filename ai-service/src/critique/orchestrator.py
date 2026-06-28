# ─────────────────────────────────────────────────────────────────
# src/critique/orchestrator.py
# ─────────────────────────────────────────────────────────────────
#
# CritiqueOrchestrator running deterministic evaluations, AI queries,
# and coordinating compilation reports.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List
from src.critique.constants import CritiqueStatus
from src.critique.models import AICritiqueObservation, InvestmentCritique
from src.critique.deterministic_engine import DeterministicCritiqueEngine
from src.critique.ai_engine import AICritiqueEngine
from src.critique.compiler import CritiqueCompiler
from src.critique.interfaces import BaseLLMService
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.intelligence.models import InvestmentIntelligence

class CritiqueOrchestrator:
    """
    Coordinates execution of deterministic stress test simulations,
    mockable LLM queries, and compiles the final InvestmentCritique payload.
    """
    @staticmethod
    def run_critique(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        intel: InvestmentIntelligence,
        llm_service: BaseLLMService
    ) -> InvestmentCritique:
        start_time = time.perf_counter()
        
        # 1. Execute Deterministic Engine (Raises runtime error on failure)
        try:
            det_out = DeterministicCritiqueEngine.evaluate(thesis, review, intel)
        except Exception as e:
            raise RuntimeError(f"Deterministic stress-test evaluation failed: {str(e)}") from e
            
        status = CritiqueStatus.SUCCESS
        ai_obs = None
        warnings: List[str] = []
        
        # 2. Execute AI Critique Engine (Gracefully degrades on timeout/parse failure)
        try:
            ai_obs = AICritiqueEngine.evaluate(thesis, review, llm_service)
        except Exception as e:
            status = CritiqueStatus.DEGRADED
            warnings.append(f"AI Critique Engine execution failed: {str(e)}. Returning deterministic stress-test results only.")
            ai_obs = AICritiqueObservation(observedAssumptions=[], observedBiases=[], observedReasoningFlaws=[])
            
        # 3. Merges and compiles the validated outputs
        critique = CritiqueCompiler.compile(det_out, ai_obs, thesis, review, status, warnings)
        
        # Set overall latency
        latency = (time.perf_counter() - start_time) * 1000.0
        
        # Re-construct metadata to set correct latency
        new_meta = critique.meta.model_copy(update={"latencyMs": round(latency, 2)})
        
        return critique.model_copy(update={"meta": new_meta})
