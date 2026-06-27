# ─────────────────────────────────────────────────────────────────
# src/api/routes/evidence.py
# ─────────────────────────────────────────────────────────────────
#
# Route definitions for structured evidence collection.
# Maps POST /collect to the coordinator service pipeline.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.services.company_service import ResolverResult
from src.services.evidence_service import collect_evidence_package
from src.utils.response import send_success, send_error
from src.constants.error_codes import AI_SERVICE_TIMEOUT

router = APIRouter()

@router.post("/collect")
def collect_evidence(payload: ResolverResult):
    """
    POST /api/v1/evidence/collect
    
    Accepts a resolved company entity (ResolverResult) and triggers the
    multi-channel structured evidence collection pipeline.
    """
    try:
        evidence_package = collect_evidence_package(payload.model_dump())
        return send_success(data=evidence_package.model_dump())
    except TimeoutError as te:
        return send_error(
            code=AI_SERVICE_TIMEOUT,
            message=str(te),
            status_code=504
        )
