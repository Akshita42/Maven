# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/risk.py
# ─────────────────────────────────────────────────────────────────
#
# RiskReviewer evaluating risk penalties and statement completeness.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.committee.constants import ReviewerType, OpinionRecommendation, ReviewStatus
from src.committee.interfaces import BaseReviewer
from src.committee.models import CommitteeOpinion
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class RiskReviewer(BaseReviewer):
    """
    Evaluates corporate operational risk indicators and validation reports status.
    """
    @property
    def reviewerId(self) -> str:
        return "RISK"

    @property
    def reviewerType(self) -> Optional[ReviewerType]:
        return ReviewerType.RISK

    @property
    def reviewerVersion(self) -> str:
        return "1.0.0"

    @property
    def rulesVersion(self) -> str:
        return "1.0.0"

    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        start_time = time.perf_counter()
        
        sec = thesis.sections.get("risk")
        
        concerns: List[str] = []
        supporting: List[str] = []
        conflicting: List[str] = []
        assumptions: List[str] = []
        missing: List[str] = []
        decision_refs: List[str] = []
        explanation_ids: List[str] = []
        
        status = ReviewStatus.SUCCESS
        coverage = 1.0
        confidence = 0.95
        
        if not sec or not sec.statements:
            status = ReviewStatus.SKIPPED
            coverage = 0.0
            confidence = 0.0
            return CommitteeOpinion(
                reviewerId=self.reviewerId,
                reviewerType=self.reviewerType,
                recommendation=OpinionRecommendation.QUESTION,
                recommendationImpact=0.0,
                confidence=confidence,
                coverageScore=coverage,
                status=status,
                concerns=["Risk section is missing in thesis."],
                supportingStatements=[],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=["risk_section"],
                decisionReferences=[],
                explanationIds=[],
                reviewerVersion=self.reviewerVersion,
                rulesVersion=self.rulesVersion,
                executionTimeMs=0.0
            )

        has_validation_failures = False
        has_coverage_failures = False
        
        for stmt in sec.statements:
            finding = stmt.finding.lower()
            supporting.append(stmt.finding)
            
            if stmt.ruleId:
                decision_refs.append(stmt.ruleId)
                explanation_ids.append(stmt.ruleId)
                
            if "failed check" in finding or "validation penalty" in finding:
                has_validation_failures = True
                concerns.append("VALIDATION RISK: Data validation rules triggered errors.")
                conflicting.append(stmt.finding)
            elif "coverage penalty" in finding or "incomplete" in finding:
                has_coverage_failures = True
                concerns.append("COVERAGE RISK: Incomplete derived statements coverage.")
                conflicting.append(stmt.finding)

        if has_validation_failures or has_coverage_failures:
            rec = OpinionRecommendation.QUESTION
            impact = -1.5
        else:
            rec = OpinionRecommendation.SUPPORT
            impact = 0.0
            
        assumptions.append("Validation limits correctly define the boundaries of GAAP metrics.")
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        return CommitteeOpinion(
            reviewerId=self.reviewerId,
            reviewerType=self.reviewerType,
            recommendation=rec,
            recommendationImpact=impact,
            confidence=confidence,
            coverageScore=coverage,
            status=status,
            concerns=deduplicate_preserve_order(concerns),
            supportingStatements=deduplicate_preserve_order(supporting),
            conflictingStatements=deduplicate_preserve_order(conflicting),
            assumptions=deduplicate_preserve_order(assumptions),
            missingEvidence=deduplicate_preserve_order(missing),
            decisionReferences=deduplicate_preserve_order(decision_refs),
            explanationIds=deduplicate_preserve_order(explanation_ids),
            reviewerVersion=self.reviewerVersion,
            rulesVersion=self.rulesVersion,
            executionTimeMs=round(latency, 2)
        )
