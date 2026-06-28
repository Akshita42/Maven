# ─────────────────────────────────────────────────────────────────
# src/api/routes/thesis.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Thesis Builder.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.intelligence.models import InvestmentIntelligence
from src.domain.contracts.evidence import EvidencePackage
from src.services.company_service import ResolverResult
from src.services.evidence_service import collect_evidence_package
from src.intelligence.orchestration import IntelligenceService
from src.thesis.builder import ThesisBuilder
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/build")
def build_thesis(payload: dict):
    """
    Coordinates building a deterministic investment thesis from an intelligence package.
    Accepts direct InvestmentIntelligence, EvidencePackage, or ResolverResult payload.
    """
    try:
        # 1. Resolve to InvestmentIntelligence
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
            
        # 2. Build InvestmentThesis using stateless builder
        thesis = ThesisBuilder.build(intelligence)
        
        return send_success(data=thesis.model_dump())
        
    except Exception as e:
        return send_error(message=f"Thesis compilation failed: {str(e)}", code=500)
