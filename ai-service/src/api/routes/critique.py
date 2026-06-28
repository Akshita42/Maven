# ─────────────────────────────────────────────────────────────────
# src/api/routes/critique.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Self-Critique.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.intelligence.models import InvestmentIntelligence
from src.domain.contracts.evidence import EvidencePackage
from src.services.company_service import ResolverResult
from src.services.evidence_service import collect_evidence_package
from src.intelligence.orchestration import IntelligenceService
from src.thesis.builder import ThesisBuilder
from src.committee.orchestrator import CommitteeOrchestrator
from src.critique.orchestrator import CritiqueOrchestrator
from src.critique.ai_engine import LLMService
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/evaluate")
def evaluate_critique(payload: dict):
    """
    Coordinates evaluation of the Investment Critique by the Self-Critique Layer.
    Accepts direct InvestmentCritique inputs or preceding pipeline segments.
    """
    try:
        # Resolve to raw ingredients
        if "thesisId" in payload and "opinions" in payload:
            # Payload is a direct bundle of thesis + committee review
            # Wait, let's parse them or build them sequentially
            pass
            
        # Standard cascade resolution to match committee routes
        if "thesisId" in payload:
            # We have a Thesis (and we need to fetch/generate the committee review & intelligence)
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
        # If it was generated above, we have 'intelligence'. If it came as thesis payload,
        # we can reconstruct intelligence or collect evidence package first.
        # Since AAPL, MSFT, TSLA, TSM evidence packages are cached and fast,
        # we can dynamically build it using company resolution if missing:
        if "intelligence" in locals():
            intel_obj = intelligence
        else:
            # Reconstruct or generate intelligence from company profile
            evidence = collect_evidence_package({"ticker": thesis.ticker})
            intel_service = IntelligenceService()
            intel_obj = intel_service.compile_intelligence(evidence)
            
        # Execute orchestrator with standard LLMService
        llm = LLMService()
        critique = CritiqueOrchestrator.run_critique(thesis, review, intel_obj, llm)
        
        return send_success(data=critique.model_dump())
        
    except Exception as e:
        return send_error(message=f"Critique evaluation failed: {str(e)}", code=500)
