# ─────────────────────────────────────────────────────────────────
# src/core/events.py
# ─────────────────────────────────────────────────────────────────
#
# Pure domain events decoupled from the transport layer.
# These events are emitted by the PipelineService and Agents.
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Any, Optional
from pydantic import BaseModel

class DomainEvent(BaseModel):
    """Base class for all domain events."""
    pass

class StageStarted(DomainEvent):
    stage: str
    message: Optional[str] = None

class StageCompleted(DomainEvent):
    stage: str
    message: Optional[str] = None

class EvidenceGenerated(DomainEvent):
    stage: str = "evidence_collection"
    evidence_summary: Dict[str, Any]

class CommitteeCompleted(DomainEvent):
    stage: str = "committee_review"
    committee_decision: Dict[str, Any]

class RecommendationGenerated(DomainEvent):
    stage: str = "recommendation"
    recommendation_data: Dict[str, Any]

class WorkflowCompleted(DomainEvent):
    report_id: str
    report_data: Dict[str, Any]
    content: Optional[str] = None

class WorkflowFailed(DomainEvent):
    stage: str
    error: str
