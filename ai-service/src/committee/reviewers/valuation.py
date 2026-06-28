# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/valuation.py
# ─────────────────────────────────────────────────────────────────
#
# ValuationReviewer evaluating valuation statements and benchmark availability.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.committee.constants import ReviewerType, OpinionRecommendation, ReviewStatus
from src.committee.interfaces import BaseReviewer
from src.committee.models import CommitteeOpinion
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class ValuationReviewer(BaseReviewer):
    """
    Evaluates corporate trading pricing, multiples, and benchmark coverage.
    """
    @property
    def reviewerId(self) -> str:
        return "VALUATION"

    @property
    def reviewerType(self) -> Optional[ReviewerType]:
        return ReviewerType.VALUATION

    @property
    def reviewerVersion(self) -> str:
        return "1.0.0"

    @property
    def rulesVersion(self) -> str:
        return "1.0.0"

    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        start_time = time.perf_counter()
        
        sec = thesis.sections.get("valuation")
        
        concerns: List[str] = []
        supporting: List[str] = []
        conflicting: List[str] = []
        assumptions: List[str] = []
        missing: List[str] = []
        decision_refs: List[str] = []
        explanation_ids: List[str] = []
        
        status = ReviewStatus.SUCCESS
        coverage = 1.0
        confidence = 0.50  # Valuation confidence is capped due to missing peers
        
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
                concerns=["Valuation section is missing in thesis."],
                supportingStatements=[],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=["valuation_section"],
                decisionReferences=[],
                explanationIds=[],
                reviewerVersion=self.reviewerVersion,
                rulesVersion=self.rulesVersion,
                executionTimeMs=0.0
            )

        for stmt in sec.statements:
            finding = stmt.finding.lower()
            supporting.append(stmt.statementId)
            
            if stmt.ruleId:
                decision_refs.append(stmt.ruleId)
                explanation_ids.append(stmt.ruleId)
                
            if "missing sector peer" in finding or "capped" in finding:
                concerns.append("Benchmark valuation databases (analyst/multiples/DCF) are missing.")
                conflicting.append(stmt.statementId)
                missing.extend(["peerMultiplesDatabase", "analystEstimates", "discountedCashFlowModelInputs"])

        rec = OpinionRecommendation.QUESTION
        impact = -1.0
        
        assumptions.append("Market pricing matches current public listing quote pages.")
        
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
