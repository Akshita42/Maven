# ─────────────────────────────────────────────────────────────────
# src/api/routes/intelligence.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Intelligence Layer.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.services.company_service import ResolverResult
from src.domain.contracts.evidence import EvidencePackage
from src.services.evidence_service import collect_evidence_package
from src.intelligence.orchestration import IntelligenceService
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/analyze")
def analyze_company(payload: dict):
    """
    Coordinates evidence collection and compiles deterministic investment intelligence.
    Accepts either an EvidencePackage directly (has evidenceId) or a ResolverResult DTO.
    """
    try:
        # Check if direct EvidencePackage is provided
        if "evidenceId" in payload:
            evidence = EvidencePackage(**payload)
        else:
            # Map resolver result DTO and collect new evidence package
            resolver_dto = ResolverResult(**payload)
            evidence = collect_evidence_package(resolver_dto.model_dump())
            
        service = IntelligenceService()
        intelligence = service.compile_intelligence(evidence)
        
        return send_success(data=intelligence.model_dump())
        
    except Exception as e:
        return send_error(message=f"Intelligence compilation failed: {str(e)}", code=500)
