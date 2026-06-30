# ─────────────────────────────────────────────────────────────────
# src/report/builder.py
# ─────────────────────────────────────────────────────────────────
#
# Deterministic Report Builder.
# Compiles all layers into a final Investment Report presentation object.
# ─────────────────────────────────────────────────────────────────

import uuid
from datetime import datetime
from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.models import InvestmentIntelligence
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.models import InvestmentRecommendation
from src.report.models import (
    InvestmentReport,
    ExecutiveSummary,
    CompanyOverview,
    ReportMetadata,
    ReportStatus
)

class ReportBuilder:
    """
    Builds the final immutable InvestmentReport by compiling upstream models.
    """
    
    @staticmethod
    def build(
        evidence: EvidencePackage,
        intelligence: InvestmentIntelligence,
        thesis: InvestmentThesis,
        committee: InvestmentCommitteeReview,
        critique: InvestmentCritique,
        recommendation: InvestmentRecommendation
    ) -> InvestmentReport:
        
        # Extract CompanyName from evidence if possible, else default to Ticker
        company_name = thesis.ticker
        if hasattr(evidence, 'companyProfile') and evidence.companyProfile and evidence.companyProfile.companyName and evidence.companyProfile.companyName.value:
            company_name = evidence.companyProfile.companyName.value

        company_overview = CompanyOverview(
            ticker=thesis.ticker,
            companyName=company_name
        )

        executive_summary = ExecutiveSummary(
            stance=recommendation.stance,
            conviction=recommendation.conviction,
            horizon=recommendation.horizon,
            overallScore=thesis.overallScore
        )

        meta = ReportMetadata(
            compiledAt=datetime.utcnow().isoformat() + "Z",
            status=ReportStatus.SUCCESS
        )

        return InvestmentReport(
            reportId=str(uuid.uuid4()),
            executiveSummary=executive_summary,
            companyOverview=company_overview,
            evidence=evidence,
            intelligence=intelligence,
            thesis=thesis,
            committee=committee,
            critique=critique,
            recommendation=recommendation,
            meta=meta
        )
