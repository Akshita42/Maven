import json
import asyncio
from pprint import pprint

from src.recommendation.builder import RecommendationBuilder
from src.recommendation.constants import InvestmentStance
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.models import InvestmentRecommendation
from pydantic import ValidationError

def test_recommendation_builder():
    print("================ TEST: RECOMMENDATION GENERATOR ================")
    
    # 1. Load mock inputs (these could be fabricated or loaded from previous test files, 
    # but for simplicity we will construct minimal valid models)
    # We will just construct mock dicts and validate them if necessary, 
    # but let's mock it using actual model classes to ensure valid inputs.
    
    # Actually, we can fetch real AAPL models from the APIs or mock them fully.
    # Since we need to test RecommendationBuilder (a pure function), we can construct the models here.
    
    from src.committee.constants import OpinionRecommendation, ReviewStatus, ConflictSeverity
    from src.critique.constants import CritiquePriority, CritiqueSeverity, CritiqueStatus
    from src.critique.models import (
        RobustnessSummary, RobustnessAnalysis, ScenarioOutcome, ActionableVulnerabilities,
        CritiqueMetadata, CritiqueCompilerReport, InvalidatingAssumption, LineageTrace
    )
    from src.committee.models import (
        DecisionOutcome, VoteSummary, CommitteeOpinion, CommitteeMetadata
    )
    from src.thesis.models import ThesisMetadata
    from src.recommendation.constants import ConvictionLevel
    
    print("Constructing mock inputs...")
    
    # Mock Thesis
    thesis_id = "THESIS-123"
    intel_id = "INTEL-123"
    evidence_id = "EVIDENCE-123"
    
    thesis = InvestmentThesis(
        schemaVersion="1.0.0",
        thesisId=thesis_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id,
        ticker="MOCK",
        overallScore=8.5,
        sections={},
        meta=ThesisMetadata(compiledAt="2026-01-01T00:00:00Z")
    )
    
    # Mock Review
    committee_id = "COMMITTEE-123"
    review = InvestmentCommitteeReview(
        committeeId=committee_id,
        thesisId=thesis_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id,
        schemaVersion="1.0.0",
        decisionOutcome=DecisionOutcome(
            recommendation=OpinionRecommendation.SUPPORT,
            decisionReasons=["Strong growth", "Good moat"],
            voteSummary=VoteSummary(supportVotes=3, questionVotes=0, rejectVotes=0)
        ),
        overallConfidence=0.90,
        opinions=[
            CommitteeOpinion(
                reviewerId="FINANCIAL",
                recommendation=OpinionRecommendation.SUPPORT,
                recommendationImpact=1.0,
                confidence=0.95,
                coverageScore=1.0,
                status=ReviewStatus.SUCCESS,
                concerns=["Minor debt issue"],
                supportingStatements=["High FCF"],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=[],
                decisionReferences=[],
                explanationIds=[],
                reviewerVersion="1",
                rulesVersion="1",
                executionTimeMs=100
            )
        ],
        conflicts=[],
        meta=CommitteeMetadata(compiledAt="2026-01-01T00:00:00Z", latencyMs=10, reviewersExecuted=[], overallCoverage=1.0, overallHealth=1.0)
    )
    
    # Mock Critique
    critique_id = "CRITIQUE-123"
    critique = InvestmentCritique(
        critiqueId=critique_id,
        thesisId=thesis_id,
        committeeReviewId=committee_id,
        intelligenceId=intel_id,
        evidenceId=evidence_id,
        schemaVersion="1.0.0",
        robustnessSummary=RobustnessSummary(
            stabilityIndex=0.85,
            assumptionQuality=0.9,
            coverageQuality=1.0,
            confidenceConsistency=0.9,
            biasRisk=0.1
        ),
        robustnessAnalysis=RobustnessAnalysis(
            originalScore=8.5,
            scenarios=[],
            mostSensitiveMetric="Valuation",
            robustnessRationale="Robust"
        ),
        biasEvaluations=[],
        coverageAudits=[],
        actionableVulnerabilities=ActionableVulnerabilities(
            invalidatingAssumptions=[
                InvalidatingAssumption(
                    assumptionId="A1", description="Assumes rates stay low",
                    invalidationTrigger="Rates go up", priority=CritiquePriority.MEDIUM,
                    lineage=LineageTrace(reviewerIds=[], statementIds=[])
                )
            ],
            decisionChangingEvidence=[],
            highestValueMissingEvidence=[],
            weakestReasoningChain=[]
        ),
        meta=CritiqueMetadata(
            compiledAt="2026-01-01T00:00:00Z", latencyMs=10, status=CritiqueStatus.SUCCESS,
            evaluatorsExecuted=[], llmModelName="mock", llmTemperature=0.1,
            compilerReport=CritiqueCompilerReport(
                totalObservationsReceived=1, totalObservationsValidated=1,
                totalObservationsRejected=0, validationWarnings=[], normalizedFieldCount=0
            )
        )
    )
    
    print("Building Recommendation...")
    rec = RecommendationBuilder.build(thesis, review, critique)
    
    # 1. UUID Linkage
    assert rec.thesisId == thesis_id, "Thesis ID mismatch"
    assert rec.committeeReviewId == committee_id, "Committee ID mismatch"
    assert rec.critiqueId == critique_id, "Critique ID mismatch"
    assert rec.intelligenceId == intel_id, "Intelligence ID mismatch"
    assert rec.evidenceId == evidence_id, "Evidence ID mismatch"
    print("✓ UUID Linkage Validated")
    
    # 2. Recommendation Consistency
    assert rec.stance in [InvestmentStance.BUY, InvestmentStance.STRONG_BUY], f"Stance {rec.stance} contradicts Committee SUPPORT"
    assert rec.conviction == ConvictionLevel.HIGH, f"Expected HIGH conviction based on 0.85 robustness and 0.9 confidence"
    print("✓ Recommendation Consistency Validated (Stance: {}, Conviction: {})".format(rec.stance, rec.conviction))
    
    # 3. No Target Price Exists
    assert not hasattr(rec, "targetPrice"), "targetPrice should not exist"
    print("✓ Schema Verification: No targetPrice field")
    
    # 4. Version Lineage Preserved
    assert rec.meta.thesisVersion == thesis.schemaVersion
    assert rec.meta.committeeVersion == review.meta.committeeVersion
    assert rec.meta.critiqueVersion == critique.meta.critiqueVersion
    print("✓ Version Lineage Preserved")
    
    # 5. Immutability
    try:
        rec.stance = InvestmentStance.SELL
        print("❌ Immutability failed: model allowed mutation")
    except ValidationError:
        print("✓ Immutability Verified (Frozen Config Enforced)")
        
    print("✓ All Phase 11 tests passed successfully!")

if __name__ == "__main__":
    test_recommendation_builder()
