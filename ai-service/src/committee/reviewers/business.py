# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/business.py
# ─────────────────────────────────────────────────────────────────
#
# BusinessReviewer evaluating thesis business overview and moats.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.committee.constants import ReviewerType, OpinionRecommendation, ReviewStatus
from src.committee.interfaces import BaseReviewer
from src.committee.models import CommitteeOpinion
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class BusinessReviewer(BaseReviewer):
    """
    Evaluates corporate business quality, moats, and operational scale.
    """
    @property
    def reviewerId(self) -> str:
        return "BUSINESS"

    @property
    def reviewerType(self) -> Optional[ReviewerType]:
        return ReviewerType.BUSINESS

    @property
    def reviewerVersion(self) -> str:
        return "1.0.0"

    @property
    def rulesVersion(self) -> str:
        return "1.0.0"

    def review(self, thesis: InvestmentThesis) -> CommitteeOpinion:
        start_time = time.perf_counter()
        
        sec = thesis.sections.get("business_quality")
        
        concerns: List[str] = []
        supporting: List[str] = []
        conflicting: List[str] = []
        assumptions: List[str] = []
        missing: List[str] = []
        decision_refs: List[str] = []
        explanation_ids: List[str] = []
        
        status = ReviewStatus.SUCCESS
        coverage = 1.0
        confidence = 0.90
        
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
                concerns=["Business Quality section is missing in thesis."],
                supportingStatements=[],
                conflictingStatements=[],
                assumptions=[],
                missingEvidence=["business_quality_section"],
                decisionReferences=[],
                explanationIds=[],
                reviewerVersion=self.reviewerVersion,
                rulesVersion=self.rulesVersion,
                executionTimeMs=0.0
            )

        # Evaluate statements preserving original ordering
        has_small_scale = False
        has_moat = False
        
        for stmt in sec.statements:
            finding = stmt.finding.lower()
            supporting.append(stmt.statementId)
            
            if stmt.ruleId:
                decision_refs.append(stmt.ruleId)
                explanation_ids.append(stmt.ruleId)
                
            if "small enterprise" in finding:
                has_small_scale = True
                concerns.append("Organizational scale is small, presenting higher key-person risk.")
                conflicting.append(stmt.statementId)
            elif "high-moat" in finding:
                has_moat = True
                
        # Determine recommendation and impact
        if has_small_scale:
            rec = OpinionRecommendation.QUESTION
            impact = -1.0
        elif has_moat:
            rec = OpinionRecommendation.SUPPORT
            impact = 0.8
        else:
            rec = OpinionRecommendation.SUPPORT
            impact = 0.0
            
        assumptions.append("Moat rating assumes sustained industry regulatory structure.")
        
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
