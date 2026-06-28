# ─────────────────────────────────────────────────────────────────
# src/committee/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable schemas for the Investment Committee Layer.
# Enforces strict type safety and frozen model configurations.
# ─────────────────────────────────────────────────────────────────

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from src.committee.constants import (
    ReviewerType,
    OpinionRecommendation,
    ReviewStatus,
    ConflictSeverity
)

class ConflictObject(BaseModel):
    """
    A structured description of a logical discrepancy, coverage drop,
    or validation issue detected across thesis sections.
    """
    model_config = ConfigDict(frozen=True)
    
    conflictId: str  # e.g., "CF-001"
    type: str
    severity: ConflictSeverity
    description: str
    involvedStatements: List[str]
    ruleReferences: List[str]
    decisionTraceReferences: List[str]

class VoteSummary(BaseModel):
    """
    A tally of reviewer recommendation votes.
    """
    model_config = ConfigDict(frozen=True)
    
    supportVotes: int
    questionVotes: int
    rejectVotes: int

class DecisionOutcome(BaseModel):
    """
    The final consolidated committee decision and rationale reasons list.
    """
    model_config = ConfigDict(frozen=True)
    
    recommendation: OpinionRecommendation
    decisionReasons: List[str]
    voteSummary: VoteSummary

class CommitteeOpinion(BaseModel):
    """
    Structured reviewer evaluation opinion.
    """
    model_config = ConfigDict(frozen=True)
    
    reviewerId: str
    reviewerType: Optional[ReviewerType] = None
    recommendation: OpinionRecommendation
    recommendationImpact: float
    confidence: float
    coverageScore: float
    status: ReviewStatus
    concerns: List[str]
    supportingStatements: List[str]
    conflictingStatements: List[str]
    assumptions: List[str]
    missingEvidence: List[str]
    decisionReferences: List[str]
    explanationIds: List[str]
    reviewerVersion: str
    rulesVersion: str
    executionTimeMs: float

class CommitteeMetadata(BaseModel):
    """
    Metadata capturing latency, coverage, and execution health metrics.
    """
    model_config = ConfigDict(frozen=True)
    
    committeeVersion: str = "1.0.0"
    votingVersion: str = "1.0.0"
    compiledAt: str
    latencyMs: float
    reviewersExecuted: List[str]
    overallCoverage: float
    overallHealth: float

class InvestmentCommitteeReview(BaseModel):
    """
    Root contract for the Investment Committee review payload.
    """
    model_config = ConfigDict(frozen=True)
    
    committeeId: str
    thesisId: str
    intelligenceId: str
    evidenceId: str
    schemaVersion: str = "1.0.0"
    decisionOutcome: DecisionOutcome
    overallConfidence: float
    opinions: List[CommitteeOpinion]
    conflicts: List[ConflictObject]
    meta: CommitteeMetadata
