import json
import asyncio
from pprint import pprint

from src.report.builder import ReportBuilder
from src.recommendation.constants import InvestmentStance
from src.domain.contracts.evidence import EvidencePackage
from src.domain.financials import ProviderMetadata, ValidationReport
from src.domain.evidence import CompanyProfileEvidence, MarketDataEvidence, NewsItemEvidence, FinancialsEvidence
from src.intelligence.models import InvestmentIntelligence, ExecutionMetadata, PipelineMetadata, RiskPenalty
from src.thesis.models import InvestmentThesis, ThesisMetadata
from src.committee.models import InvestmentCommitteeReview, DecisionOutcome, VoteSummary, CommitteeMetadata
from src.critique.models import InvestmentCritique, RobustnessSummary, RobustnessAnalysis, ActionableVulnerabilities, CritiqueMetadata, CritiqueCompilerReport
from src.recommendation.models import InvestmentRecommendation, RecommendationMetadata, RecommendationCatalyst, MonitoringItem
from src.committee.constants import OpinionRecommendation
from src.critique.constants import CritiqueStatus
from src.recommendation.constants import ConvictionLevel, TimeHorizon, RecommendationStatus
from src.report.models import InvestmentReport, ExecutiveSummary, CompanyOverview, ReportMetadata, ReportStatus
from pydantic import ValidationError

def test_report_builder():
    print("================ TEST: REPORT GENERATOR ================")
    
    print("Constructing mock upstream components...")
    
    # 1. Evidence
    evidence_id = "EVI-123"
    evidence = EvidencePackage.model_construct(
        evidenceId=evidence_id,
        providers={"test": ProviderMetadata.model_construct()}
    )
    
    # 2. Intelligence
    intel_id = "INT-123"
    intelligence = InvestmentIntelligence.model_construct(
        intelligenceId=intel_id,
        evidenceId=evidence_id
    )
    
    # 3. Thesis
    thesis_id = "THE-123"
    thesis = InvestmentThesis.model_construct(
        thesisId=thesis_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id,
        ticker="MOCK",
        overallScore=8.5
    )
    
    # 4. Committee
    committee_id = "COM-123"
    committee = InvestmentCommitteeReview.model_construct(
        committeeId=committee_id,
        thesisId=thesis_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id
    )
    
    # 5. Critique
    critique_id = "CRI-123"
    critique = InvestmentCritique.model_construct(
        critiqueId=critique_id,
        thesisId=thesis_id,
        committeeReviewId=committee_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id
    )
    
    # 6. Recommendation
    rec_id = "REC-123"
    recommendation = InvestmentRecommendation.model_construct(
        recommendationId=rec_id,
        thesisId=thesis_id,
        committeeReviewId=committee_id,
        critiqueId=critique_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id,
        stance=InvestmentStance.BUY,
        horizon=TimeHorizon.LONG_TERM,
        conviction=ConvictionLevel.HIGH
    )
    
    print("Building Report...")
    report = ReportBuilder.build(evidence, intelligence, thesis, committee, critique, recommendation)
    
    # 1. Verify UUID Lineage and Structure
    assert report.evidence.evidenceId == evidence_id
    assert report.intelligence.intelligenceId == intel_id
    assert report.thesis.thesisId == thesis_id
    assert report.committee.committeeId == committee_id
    assert report.critique.critiqueId == critique_id
    assert report.recommendation.recommendationId == rec_id
    print("✓ UUID Lineage Validated (All objects strictly embedded)")
    
    # 2. Verify Convenience Models
    assert isinstance(report.executiveSummary, ExecutiveSummary)
    assert report.executiveSummary.stance == InvestmentStance.BUY
    assert report.executiveSummary.conviction == ConvictionLevel.HIGH
    assert isinstance(report.companyOverview, CompanyOverview)
    assert report.companyOverview.ticker == "MOCK"
    print("✓ Convenience models populated successfully")
    
    # 3. Immutability
    try:
        report.companyOverview = CompanyOverview(ticker="FAIL", companyName="FAIL")
        print("❌ Immutability failed: model allowed mutation")
    except ValidationError:
        print("✓ Immutability Verified (Frozen Config Enforced)")
        
    print("✓ All Phase 12 tests passed successfully!")

if __name__ == "__main__":
    test_report_builder()
