# ─────────────────────────────────────────────────────────────────
# src/api/routes/committee.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Committee Review.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.thesis.models import InvestmentThesis
from src.intelligence.models import InvestmentIntelligence
from src.domain.contracts.evidence import EvidencePackage
from src.services.company_service import ResolverResult
from src.services.evidence_service import collect_evidence_package
from src.intelligence.orchestration import IntelligenceService
from src.thesis.builder import ThesisBuilder
from src.committee.orchestrator import CommitteeOrchestrator
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/review")
def review_thesis(payload: dict):
    """
    Coordinates review of the Investment Thesis by the deterministic Investment Committee.
    Accepts direct InvestmentThesis, InvestmentIntelligence, EvidencePackage, or ResolverResult.
    """
    try:
        # 1. Resolve to InvestmentThesis
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
            
        # 2. Execute dynamic Investment Committee orchestrator
        review = CommitteeOrchestrator.run_review(thesis)
        
        return send_success(data=review.model_dump())
        
    except Exception as e:
        return send_error(message=f"Committee review failed: {str(e)}", code=500)
