# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/governance.py
# ─────────────────────────────────────────────────────────────────
#
# GovernanceReviewer evaluating exchange compliance and registry records.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.committee.constants import ReviewerType, OpinionRecommendation, ReviewStatus
from src.committee.interfaces import BaseReviewer
from src.committee.models import CommitteeOpinion
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class GovernanceReviewer(BaseReviewer):
    """
    Evaluates corporate regulatory exchange listing safety and compliance logs.
    """
    @property
    def reviewerId(self) -> str:
        return "GOVERNANCE"

    @property
    def reviewerType(self) -> Optional[ReviewerType]:
        return ReviewerType.GOVERNANCE

    @property
    def reviewerVersion(self) -> str:
        return "1.0.0"

    @property
    def rulesVersion(self) -> str:
        return "1.0.0"

    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        start_time = time.perf_counter()
        
        sec = thesis.sections.get("management")
        
        concerns: List[str] = []
        supporting: List[str] = []
        conflicting: List[str] = []
        assumptions: List[str] = []
        missing: List[str] = []
        decision_refs: List[str] = []
        explanation_ids: List[str] = []
        
        status = ReviewStatus.SUCCESS
        coverage = 1.0
        confidence = 0.50  # Capped qualitative confidence
        
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
                concerns=["Management Assessment section is missing in thesis."],
                supportingStatements=[],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=["management_section"],
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
                
            if "missing qualitative" in finding or "capped" in finding:
                concerns.append("Board registry and executive compensation committees files are missing.")
                conflicting.append(stmt.statementId)
                missing.extend(["boardOfDirectorsRegistry", "compensationCommitteeLogs"])

        rec = OpinionRecommendation.QUESTION
        impact = -1.0
        
        assumptions.append("Exchange listing regulations satisfy standard corporate safety compliance.")
        
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
