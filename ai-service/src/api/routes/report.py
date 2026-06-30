# ─────────────────────────────────────────────────────────────────
# src/api/routes/report.py
# ─────────────────────────────────────────────────────────────────
#
# FastAPI API endpoints router for the Report Generator Layer.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, Query
from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.models import InvestmentIntelligence
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.models import InvestmentRecommendation
from src.report.builder import ReportBuilder
from src.report.service import ReportService
from src.utils.response import send_success, send_error

router = APIRouter()

@router.post("/build")
def build_report(payload: dict):
    """
    Builds the final InvestmentReport deterministically by embedding
    all upstream components.
    """
    try:
        required_keys = ["evidence", "intelligence", "thesis", "committee", "critique", "recommendation"]
        for key in required_keys:
            if key not in payload:
                return send_error(message=f"Payload must contain '{key}' object.", code=400)
            
        evidence = EvidencePackage(**payload["evidence"])
        intelligence = InvestmentIntelligence(**payload["intelligence"])
        thesis = InvestmentThesis(**payload["thesis"])
        review = InvestmentCommitteeReview(**payload["committee"])
        critique = InvestmentCritique(**payload["critique"])
        recommendation = InvestmentRecommendation(**payload["recommendation"])
        
        report = ReportBuilder.build(evidence, intelligence, thesis, review, critique, recommendation)
        
        return send_success(data=report.model_dump())
        
    except Exception as e:
        return send_error(message=f"Report compilation failed: {str(e)}", code=500)

@router.get("/latest")
async def get_latest_report(sessionId: str = Query(..., description="The session ID to retrieve the latest report for")):
    """
    GET /api/v1/report/latest?sessionId=...
    Retrieves the most recent persisted report for the given session.
    """
    report = ReportService.get_latest(sessionId)
    if not report:
        raise HTTPException(status_code=404, detail="No reports found for this session")
    return send_success(data=report)

@router.get("/{report_id}")
async def get_report(report_id: str):
    """
    GET /api/v1/report/{report_id}
    Retrieves a specific persisted report by its ID.
    """
    report = ReportService.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return send_success(data=report)
