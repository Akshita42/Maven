# ─────────────────────────────────────────────────────────────────
# src/api/routes/recommendation.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Investment Recommendation Layer.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.builder import RecommendationBuilder
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/build")
def build_recommendation(payload: dict):
    """
    Builds the final InvestmentRecommendation deterministically from
    Thesis, CommitteeReview, and Critique models.
    """
    try:
        if "thesis" not in payload or "review" not in payload or "critique" not in payload:
            return send_error(message="Payload must contain 'thesis', 'review', and 'critique' objects.", code=400)
            
        thesis = InvestmentThesis(**payload["thesis"])
        review = InvestmentCommitteeReview(**payload["review"])
        critique = InvestmentCritique(**payload["critique"])
        
        recommendation = RecommendationBuilder.build(thesis, review, critique)
        
        return send_success(data=recommendation.model_dump())
        
    except Exception as e:
        return send_error(message=f"Recommendation building failed: {str(e)}", code=500)
