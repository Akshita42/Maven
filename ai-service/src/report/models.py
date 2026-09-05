# ─────────────────────────────────────────────────────────────────
# src/report/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable domain models for the final Investment Report.
# ─────────────────────────────────────────────────────────────────

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from src.report.constants import ReportStatus
from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.models import InvestmentIntelligence
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.models import InvestmentRecommendation
from src.recommendation.constants import InvestmentStance, ConvictionLevel, TimeHorizon

class ExecutiveSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    stance: InvestmentStance
    conviction: ConvictionLevel
    horizon: TimeHorizon
    overallScore: float

class CompanyOverview(BaseModel):
    model_config = ConfigDict(frozen=True)
    ticker: str
    companyName: str

class ReportMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    schemaVersion: str = "1.0.0"
    compiledAt: str
    status: ReportStatus

class InvestmentReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    reportId: str
    schemaVersion: str = "1.0.0"
    
    # Key extracted summaries for convenience
    executiveSummary: ExecutiveSummary
    companyOverview: CompanyOverview
    
    # Upstream models embedded
    evidence: EvidencePackage
    intelligence: InvestmentIntelligence
    thesis: InvestmentThesis
    committee: InvestmentCommitteeReview
    critique: InvestmentCritique
    recommendation: InvestmentRecommendation
    
    # Adversarial Debate & Observability Extensions
    bullCase: Optional[Dict[str, Any]] = None
    bearCase: Optional[Dict[str, Any]] = None
    debateTranscript: Optional[List[Dict[str, Any]]] = None
    observability: Optional[Dict[str, Any]] = None
    
    meta: ReportMetadata
