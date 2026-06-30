# ─────────────────────────────────────────────────────────────────
# src/api/adapters/sse_adapter.py
# ─────────────────────────────────────────────────────────────────
#
# Translates abstract DomainEvents into concrete SSE JSON payloads.
# ─────────────────────────────────────────────────────────────────

import json
from datetime import datetime
from src.core.execution_context import ExecutionObserver
from src.core.events import (
    DomainEvent, StageStarted, StageCompleted, 
    EvidenceGenerated, CommitteeCompleted, 
    RecommendationGenerated, WorkflowCompleted, WorkflowFailed
)
import asyncio

class SSEEventAdapter(ExecutionObserver):
    """
    Implements ExecutionObserver.
    Pushes formatted SSE payload dictionaries onto an asyncio.Queue.
    """
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop, session_id: str, request_id: str, workflow_id: str):
        self.queue = queue
        self.loop = loop
        self.session_id = session_id
        self.request_id = request_id
        self.workflow_id = workflow_id

    def on_event(self, event: DomainEvent) -> None:
        payload = {
            "sessionId": self.session_id,
            "requestId": self.request_id,
            "workflowId": self.workflow_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if isinstance(event, StageStarted):
            payload.update({
                "type": "stage",
                "stage": event.stage,
                "status": "running"
            })
            if event.message:
                payload["message"] = event.message
                
        elif isinstance(event, StageCompleted):
            payload.update({
                "type": "stage",
                "stage": event.stage,
                "status": "completed"
            })
            if event.message:
                payload["message"] = event.message
                
        elif isinstance(event, EvidenceGenerated):
            payload.update({
                "type": "evidence",
                "data": event.evidence_summary
            })
            
        elif isinstance(event, CommitteeCompleted):
            payload.update({
                "type": "committee",
                "data": event.committee_decision
            })
            
        elif isinstance(event, RecommendationGenerated):
            payload.update({
                "type": "recommendation",
                "data": event.recommendation_data
            })
            
        elif isinstance(event, WorkflowCompleted):
            payload.update({
                "type": "completed",
                "reportId": event.report_id,
                "data": event.report_data
            })
            if event.content:
                payload["content"] = event.content
            
        elif isinstance(event, WorkflowFailed):
            payload.update({
                "type": "error",
                "stage": event.stage,
                "error": event.error
            })
            
        # Safely push to the asyncio.Queue from the background thread
        print(f"FIRST event emitted (or subsequent): {payload.get('type')}")
        self.loop.call_soon_threadsafe(self.queue.put_nowait, payload)
