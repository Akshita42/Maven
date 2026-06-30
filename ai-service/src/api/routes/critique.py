# ─────────────────────────────────────────────────────────────────
# src/api/routes/critique.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Self-Critique.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.critique.orchestrator import CritiqueOrchestrator
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/evaluate")
def evaluate_critique(payload: dict):
    """
    Coordinates evaluation of the Investment Critique by the Self-Critique Layer.
    Accepts direct InvestmentCritique inputs or preceding pipeline segments.
    """
    try:
        critique = CritiqueOrchestrator.resolve_and_run(payload)
        return send_success(data=critique.model_dump())
        
    except Exception as e:
        return send_error(message=f"Critique evaluation failed: {str(e)}", code=500)
