# ─────────────────────────────────────────────────────────────────
# src/core/execution_context.py
# ─────────────────────────────────────────────────────────────────
#
# Encapsulates all runtime/system concerns so they do not leak
# into the domain AgentState.
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.core.events import DomainEvent
from src.agent.models import AgentExecutionBudget

class ExecutionObserver(ABC):
    """
    Interface for observing domain events.
    Implemented by the SSE Transport adapter.
    """
    @abstractmethod
    def on_event(self, event: DomainEvent) -> None:
        pass

class CancellationToken:
    """Thread-safe cancellation token."""
    def __init__(self):
        self._cancelled = False
        
    def cancel(self) -> None:
        self._cancelled = True
        
    def is_cancelled(self) -> bool:
        return self._cancelled

class ExecutionContext:
    """
    Encapsulates all runtime context required during a single 
    orchestrator workflow execution.
    """
    def __init__(
        self,
        request_id: str,
        workflow_id: str,
        session_id: str,
        observer: ExecutionObserver,
        logger: Any,
        budget: AgentExecutionBudget,
        cancellation_token: CancellationToken
    ):
        self.request_id = request_id
        self.workflow_id = workflow_id
        self.session_id = session_id
        self.observer = observer
        self.logger = logger
        self.budget = budget
        self.cancellation_token = cancellation_token
        self.metrics: Dict[str, Any] = {}
