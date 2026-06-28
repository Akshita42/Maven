# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/financial.py
# ─────────────────────────────────────────────────────────────────
#
# FinancialReviewer evaluating financial health, leverage and solvency.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.committee.constants import ReviewerType, OpinionRecommendation, ReviewStatus
from src.committee.interfaces import BaseReviewer
from src.committee.models import CommitteeOpinion
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class FinancialReviewer(BaseReviewer):
    """
    Evaluates corporate liquidity, debt leverage, and capital efficiency.
    """
    @property
    def reviewerId(self) -> str:
        return "FINANCIAL"

    @property
    def reviewerType(self) -> Optional[ReviewerType]:
        return ReviewerType.FINANCIAL

    @property
    def reviewerVersion(self) -> str:
        return "1.0.0"

    @property
    def rulesVersion(self) -> str:
        return "1.0.0"

    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        start_time = time.perf_counter()
        
        sec = thesis.sections.get("financial_health")
        
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
                concerns=["Financial Health section is missing in thesis."],
                supportingStatements=[],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=["financial_health_section"],
                decisionReferences=[],
                explanationIds=[],
                reviewerVersion=self.reviewerVersion,
                rulesVersion=self.rulesVersion,
                executionTimeMs=0.0
            )

        has_solvency_risk = False
        has_compressed_margins = False
        has_liquidity_risk = False
        
        for stmt in sec.statements:
            finding = stmt.finding.lower()
            supporting.append(stmt.statementId)
            
            if stmt.ruleId:
                decision_refs.append(stmt.ruleId)
                explanation_ids.append(stmt.ruleId)
                
            if "excessive solvency risk" in finding or "excessive debt" in finding:
                has_solvency_risk = True
                concerns.append("SOLVENCY RISK: High debt leverage exceeds acceptable threshold parameters.")
                conflicting.append(stmt.statementId)
            elif "compressed" in finding:
                has_compressed_margins = True
                concerns.append("MARGIN RISK: Operating margins are compressed.")
                conflicting.append(stmt.statementId)
            elif "inadequate liquid" in finding:
                has_liquidity_risk = True
                concerns.append("LIQUIDITY RISK: Inadequate current liquid buffer detected.")
                conflicting.append(stmt.statementId)

        # Determine recommendation and impact
        if has_solvency_risk:
            rec = OpinionRecommendation.REJECT
            impact = -2.0
        elif has_compressed_margins or has_liquidity_risk:
            rec = OpinionRecommendation.QUESTION
            impact = -1.0
        else:
            rec = OpinionRecommendation.SUPPORT
            impact = 1.0
            
        assumptions.append("Balance sheet accuracy is assumed for debt ratios computation.")
        
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
