# ─────────────────────────────────────────────────────────────────
# src/api/routes/company.py
# ─────────────────────────────────────────────────────────────────
#
# Route definitions for company entity resolution.
# Maps POST /resolve to the resolution service pipeline.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from pydantic import BaseModel, Field
from src.services.company_service import resolve_company_metadata
from src.utils.response import send_success, send_error
from src.constants.error_codes import AI_SERVICE_TIMEOUT

router = APIRouter()

class ResolveRequest(BaseModel):
    """
    Validates request payload.
    Empty queries ("") or spaces are rejected by Pydantic min_length checks.
    """
    company: str = Field(
        ...,
        min_length=1,
        description="Company name or ticker symbol to resolve."
    )

    # Clean query input before validation
    model_config = {
        "str_strip_whitespace": True
    }

@router.post("/resolve")
def resolve_company(payload: ResolveRequest):
    """
    POST /api/v1/company/resolve
    
    Receives user query and resolves it to a single canonical company identity.
    Handles unknown and ambiguous inputs by setting resolved=False.
    Catches and handles TimeoutError gracefully.
    """
    try:
        resolved_result = resolve_company_metadata(payload.company)
        
        # Exclude processingTimeMs from the data block, moving it to meta
        data_dict = resolved_result.model_dump(exclude={"processingTimeMs"})
        
        return send_success(
            data=data_dict,
            meta={"processingTimeMs": resolved_result.processingTimeMs}
        )
    except TimeoutError as te:
        # Gracefully handle timeouts with a controlled error response
        return send_error(
            code=AI_SERVICE_TIMEOUT,
            message=str(te),
            status_code=504
        )
