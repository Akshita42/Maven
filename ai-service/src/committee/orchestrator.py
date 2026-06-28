# ─────────────────────────────────────────────────────────────────
# src/committee/orchestrator.py
# ─────────────────────────────────────────────────────────────────
#
# CommitteeOrchestrator pulling reviewers dynamically and running review.
# ─────────────────────────────────────────────────────────────────

import time
import uuid
from datetime import datetime
from typing import List, Dict

from src.committee.registry import ReviewerRegistry
from src.committee.voting import VotingEngine
from src.committee.constants import ReviewStatus, ConflictSeverity, OpinionRecommendation
from src.committee.models import (
    ConflictObject,
    CommitteeOpinion,
    CommitteeMetadata,
    InvestmentCommitteeReview
)
from src.thesis.models import InvestmentThesis
from src.committee.utils import deduplicate_preserve_order

class CommitteeOrchestrator:
    """
    Orchestrates the sequential evaluation of the InvestmentThesis by
    delegating to the dynamic ReviewerRegistry and VotingEngine.
    """
    @staticmethod
    def run_review(thesis: InvestmentThesis) -> InvestmentCommitteeReview:
        start_time = time.perf_counter()
        
        # 1. Fetch dynamically registered reviewers
        reviewers = ReviewerRegistry.get_reviewers()
        
        opinions: List[CommitteeOpinion] = []
        reviewers_executed: List[str] = []
        
        # 2. Sequentially execute all registered reviewers
        for rev in reviewers:
            opinions.append(rev.review(thesis))
            reviewers_executed.append(rev.reviewerId)
            
        # 3. Call Voting Engine to determine DecisionOutcome
        decision = VotingEngine.compute_outcome(opinions)
        
        # 4. Compute overall statistics
        confidences = [op.confidence for op in opinions]
        overall_conf = round(sum(confidences) / len(confidences), 4) if confidences else 1.0
        
        coverages = [op.coverageScore for op in opinions]
        overall_cov = round(sum(coverages) / len(coverages), 4) if coverages else 1.0
        
        success_reviews = sum(1 for op in opinions if op.status == ReviewStatus.SUCCESS)
        total_reviews = len(opinions)
        success_fraction = (success_reviews / total_reviews) if total_reviews > 0 else 1.0
        
        # overallHealth quality score: success rate (40%) + coverage (30%) + confidence (30%)
        overall_health = round((success_fraction * 0.40) + (overall_cov * 0.30) + (overall_conf * 0.30), 4)
        
        # 5. Perform Conflict Detection with stable IDs (CF-001, CF-002, etc.)
        conflicts: List[ConflictObject] = []
        conflict_idx = 1
        
        def add_conflict(c_type: str, severity: ConflictSeverity, description: str, statements: List[str], rules: List[str], traces: List[str]):
            nonlocal conflict_idx
            conflicts.append(ConflictObject(
                conflictId=f"CF-{conflict_idx:03d}",
                type=c_type,
                severity=severity,
                description=description,
                involvedStatements=deduplicate_preserve_order(statements),
                ruleReferences=deduplicate_preserve_order(rules),
                decisionTraceReferences=deduplicate_preserve_order(traces)
            ))
            conflict_idx += 1

        # Conflict CF-001: Contradictory Recommendations (Divergence)
        has_support = any(op.recommendation == OpinionRecommendation.SUPPORT for op in opinions)
        has_reject = any(op.recommendation == OpinionRecommendation.REJECT for op in opinions)
        if has_support and has_reject:
            involved_stmts = []
            involved_rules = []
            involved_traces = []
            for op in opinions:
                if op.recommendation in [OpinionRecommendation.SUPPORT, OpinionRecommendation.REJECT]:
                    involved_stmts.extend(op.supportingStatements + op.conflictingStatements)
                    involved_rules.extend(op.decisionReferences)
                    involved_traces.extend(op.explanationIds)
            add_conflict(
                c_type="ContradictoryRecommendations",
                severity=ConflictSeverity.CRITICAL,
                description="Reviewer recommendations display divergent opinions (both SUPPORT and REJECT present).",
                statements=involved_stmts,
                rules=involved_rules,
                traces=involved_rules
            )

        # Conflict CF-002: Low Coverage Detection
        low_cov_reviewers = [op for op in opinions if op.coverageScore < 1.0]
        if low_cov_reviewers:
            involved_stmts = []
            involved_rules = []
            for op in low_cov_reviewers:
                involved_stmts.extend(op.supportingStatements + op.conflictingStatements)
                involved_rules.extend(op.decisionReferences)
            add_conflict(
                c_type="LowEvidenceCoverage",
                severity=ConflictSeverity.WARNING,
                description="Deducted coverage score flagged by one or more committee reviewers.",
                statements=involved_stmts,
                rules=involved_rules,
                traces=involved_rules
            )

        # Conflict CF-003: Validation Penalties Detection
        has_validation_warnings = False
        involved_stmts = []
        involved_rules = []
        for op in opinions:
            if op.reviewerId == "RISK" and op.status == ReviewStatus.SUCCESS:
                # Check concerns
                if any("validation" in c.lower() or "coverage" in c.lower() for c in op.concerns):
                    has_validation_warnings = True
                    involved_stmts.extend(op.supportingStatements + op.conflictingStatements)
                    involved_rules.extend(op.decisionReferences)
        if has_validation_warnings:
            add_conflict(
                c_type="ValidationIssuesPresent",
                severity=ConflictSeverity.WARNING,
                description="Validation reports triggered rule failures or statements completeness penalties.",
                statements=involved_stmts,
                rules=involved_rules,
                traces=involved_rules
            )

        # Conflict CF-004: Weak Overall Confidence
        if overall_conf < 0.70:
            involved_stmts = []
            involved_rules = []
            for op in opinions:
                involved_stmts.extend(op.supportingStatements + op.conflictingStatements)
                involved_rules.extend(op.decisionReferences)
            add_conflict(
                c_type="WeakOverallConfidence",
                severity=ConflictSeverity.INFO,
                description="Overall committee confidence is low due to qualitative database gaps.",
                statements=involved_stmts,
                rules=involved_rules,
                traces=involved_rules
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        
        meta = CommitteeMetadata(
            committeeVersion="1.0.0",
            votingVersion="1.0.0",
            compiledAt=datetime.utcnow().isoformat() + "Z",
            latencyMs=round(latency, 2),
            reviewersExecuted=reviewers_executed,
            overallCoverage=overall_cov,
            overallHealth=overall_health
        )
        
        return InvestmentCommitteeReview(
            committeeId=str(uuid.uuid4()),
            thesisId=thesis.thesisId,
            intelligenceId=thesis.intelligenceId,
            evidenceId=thesis.evidenceId,
            schemaVersion="1.0.0",
            decisionOutcome=decision,
            overallConfidence=overall_conf,
            opinions=opinions,
            conflicts=conflicts,
            meta=meta
        )
