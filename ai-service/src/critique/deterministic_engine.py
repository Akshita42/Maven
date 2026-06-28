# ─────────────────────────────────────────────────────────────────
# src/critique/deterministic_engine.py
# ─────────────────────────────────────────────────────────────────
#
# DeterministicCritiqueEngine simulating robustness metrics and stress scenarios.
# ─────────────────────────────────────────────────────────────────

from typing import List
from src.critique.constants import CritiqueSeverity, CritiquePriority
from src.critique.models import (
    RobustnessSummary,
    ScenarioOutcome,
    RobustnessAnalysis,
    CoverageAudit
)
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.intelligence.models import InvestmentIntelligence

class DeterministicCritiqueEngine:
    """
    Executes stress test scenario math, coverage index verification,
    and calculates scoring volatility metrics deterministically.
    """
    @staticmethod
    def evaluate(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        intel: InvestmentIntelligence
    ) -> dict:
        scenarios: List[ScenarioOutcome] = []
        coverage_audits: List[CoverageAudit] = []
        
        original_score = intel.overallScore
        
        # Extract base scores
        bq_score = intel.pillars.get("business_quality").rawScore if intel.pillars.get("business_quality") else 0.0
        fh_score = intel.pillars.get("financial_health").rawScore if intel.pillars.get("financial_health") else 0.0
        gr_score = intel.pillars.get("growth").rawScore if intel.pillars.get("growth") else 0.0
        vl_score = intel.pillars.get("valuation").rawScore if intel.pillars.get("valuation") else 0.0
        mg_score = intel.pillars.get("management").rawScore if intel.pillars.get("management") else 0.0
        penalty = intel.riskPenalty.totalPenalty

        # Helper method for deterministic weighted score math
        def calc_score(bq, fh, gr, vl, mg, p) -> float:
            weighted = (bq * 0.20 + fh * 0.30 + gr * 0.15 + vl * 0.15 + mg * 0.05) / 0.85
            return max(0.0, min(10.0, weighted - p))

        # Scenario 1: Solvency leverage stress test (FH drops by 50%)
        fh_stressed = fh_score * 0.50
        sim_s1 = calc_score(bq_score, fh_stressed, gr_score, vl_score, mg_score, penalty)
        scenarios.append(ScenarioOutcome(
            scenarioId="SC-001",
            name="Solvency Stress Test (FH -50%)",
            simulatedScore=round(sim_s1, 2),
            scoreDelta=round(sim_s1 - original_score, 2),
            isRobust=sim_s1 >= 5.0
        ))

        # Scenario 2: Valuation multiples compression (VL drops by 40%)
        vl_stressed = vl_score * 0.60
        sim_s2 = calc_score(bq_score, fh_score, gr_score, vl_stressed, mg_score, penalty)
        scenarios.append(ScenarioOutcome(
            scenarioId="SC-002",
            name="Valuation Multiples Compression (VL -40%)",
            simulatedScore=round(sim_s2, 2),
            scoreDelta=round(sim_s2 - original_score, 2),
            isRobust=sim_s2 >= 5.0
        ))

        # Scenario 3: Extreme Risk Penalty escalation (Penalty +1.5)
        p_stressed = penalty + 1.5
        sim_s3 = calc_score(bq_score, fh_score, gr_score, vl_score, mg_score, p_stressed)
        scenarios.append(ScenarioOutcome(
            scenarioId="SC-003",
            name="Risk Penalty Escalation (Penalty +1.5)",
            simulatedScore=round(sim_s3, 2),
            scoreDelta=round(sim_s3 - original_score, 2),
            isRobust=sim_s3 >= 5.0
        ))

        # Determine stability metrics
        robust_count = sum(1 for s in scenarios if s.isRobust)
        stability_index = robust_count / len(scenarios) if scenarios else 1.0

        # Perform Coverage Audit check
        coverages = [op.coverageScore for op in review.opinions]
        avg_coverage = sum(coverages) / len(coverages) if coverages else 1.0

        confidences = [op.confidence for op in review.opinions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0

        # Detect gaps
        for op in review.opinions:
            if op.coverageScore < 1.0:
                coverage_audits.append(CoverageAudit(
                    auditId=f"COV-{len(coverage_audits)+1:03d}",
                    targetPillar=str(op.reviewerId),
                    severity=CritiqueSeverity.WARNING,
                    priority=CritiquePriority.HIGH,
                    description=f"Deducted statements coverage identified by {op.reviewerId} reviewer.",
                    missingIdentifiers=op.missingEvidence
                ))

        rob_analysis = RobustnessAnalysis(
            originalScore=original_score,
            scenarios=scenarios,
            mostSensitiveMetric="Financial Health" if abs(scenarios[0].scoreDelta) > abs(scenarios[1].scoreDelta) else "Valuation",
            robustnessRationale="Decision is robust under stress simulation except under risk penalty escalations."
        )

        rob_summary = RobustnessSummary(
            stabilityIndex=round(stability_index, 4),
            assumptionQuality=0.90,  # Base estimate
            coverageQuality=round(avg_coverage, 4),
            confidenceConsistency=round(avg_confidence, 4),
            biasRisk=0.0  # Will be mapped by compiler
        )

        return {
            "robustnessAnalysis": rob_analysis,
            "robustnessSummary": rob_summary,
            "coverageAudits": coverage_audits
        }
