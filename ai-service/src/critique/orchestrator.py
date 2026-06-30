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
from src.infrastructure.llm.factory import LLMFactory
from src.critique.compiler import CritiqueCompiler
from src.critique.interfaces import BaseLLMService
from src.thesis.models import InvestmentThesis
from src.thesis.builder import ThesisBuilder
from src.committee.models import InvestmentCommitteeReview
from src.committee.orchestrator import CommitteeOrchestrator
from src.intelligence.models import InvestmentIntelligence
from src.intelligence.orchestration import IntelligenceService
from src.domain.contracts.evidence import EvidencePackage
from src.services.company_service import ResolverResult
from src.services.evidence_service import collect_evidence_package

class CritiqueOrchestrator:
    """
    Coordinates execution of deterministic stress test simulations,
    mockable LLM queries, and compiles the final InvestmentCritique payload.
    """
    @staticmethod
    def resolve_and_run(payload: dict) -> InvestmentCritique:
        # Standard cascade resolution to match committee routes
        if "thesisId" in payload:
            thesis = InvestmentThesis(**payload)
        else:
            if "intelligenceId" in payload:
                intelligence = InvestmentIntelligence(**payload)
            else:
                if "evidenceId" in payload:
                    evidence = EvidencePackage(**payload)
                else:
                    resolver_dto = ResolverResult(**payload)
                    evidence = collect_evidence_package(resolver_dto.model_dump())
                    
                intel_service = IntelligenceService()
                intelligence = intel_service.compile_intelligence(evidence)
                
            thesis = ThesisBuilder.build(intelligence)
            
        # Generate the required committee review (or construct it if present in payload)
        if "committeeId" in payload:
            review = InvestmentCommitteeReview(**payload)
        else:
            review = CommitteeOrchestrator.run_review(thesis)
            
        # Re-resolve intelligence for score stress testing
        if "intelligence" in locals():
            intel_obj = locals()["intelligence"]
        else:
            evidence = collect_evidence_package({"ticker": thesis.ticker})
            intel_service = IntelligenceService()
            intel_obj = intel_service.compile_intelligence(evidence)
            
        llm = LLMFactory.get_llm_service()
        return CritiqueOrchestrator.run_critique(thesis, review, intel_obj, llm)
    @staticmethod
    def run_critique(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        intel: InvestmentIntelligence,
        llm_service: BaseLLMService
    ) -> InvestmentCritique:
        print("ENTER CritiqueOrchestrator.run_critique")
        start_time = time.perf_counter()
        
        # 1. Execute Deterministic Engine (Raises runtime error on failure)
        try:
            det_out = DeterministicCritiqueEngine.evaluate(thesis, review, intel)
        except Exception as e:
            raise RuntimeError(f"Deterministic stress-test evaluation failed: {str(e)}") from e
            
        status = CritiqueStatus.SUCCESS
        ai_obs = None
        prompt_v = None
        prompt_h = None
        warnings: List[str] = []
        
        # 2. Execute AI Critique Engine (Gracefully degrades on timeout/parse failure)
        try:
            ai_obs, prompt_v, prompt_h = AICritiqueEngine.evaluate(thesis, review, llm_service)
        except Exception as e:
            print(f"CritiqueOrchestrator caught exception from AICritiqueEngine: {e}")
            import traceback
            traceback.print_exc()
            status = CritiqueStatus.DEGRADED
            warnings.append(f"AI Critique Engine execution failed: {str(e)}. Returning deterministic stress-test results only.")
            ai_obs = AICritiqueObservation(observedAssumptions=[], observedBiases=[], observedReasoningFlaws=[])
            
        # Extract llm_service attributes safely
        tokens_used = getattr(llm_service, "last_tokens_used", None)
        finish_reason = getattr(llm_service, "last_finish_reason", None)
        model_name = getattr(llm_service, "model_name", "mock-model")

        # 3. Merges and compiles the validated outputs
        print("CritiqueOrchestrator: calling CritiqueCompiler")
        critique = CritiqueCompiler.compile(
            det_out, ai_obs, thesis, review, status, warnings,
            prompt_version=prompt_v,
            prompt_hash=prompt_h,
            finish_reason=finish_reason,
            tokens_used=tokens_used,
            llm_model_name=model_name
        )
        print("CritiqueCompiler returned successfully")
        
        # Set overall latency
        latency = (time.perf_counter() - start_time) * 1000.0
        
        # Re-construct metadata to set correct latency
        new_meta = critique.meta.model_copy(update={"latencyMs": round(latency, 2)})
        
        result = critique.model_copy(update={"meta": new_meta})
        
        elapsed = time.perf_counter() - start_time
        print("EXIT CritiqueOrchestrator.run_critique")
        print(f"Elapsed time: {elapsed:.3f}s")
        print(f"Returned object type: {type(result).__name__}")
        
        return result
