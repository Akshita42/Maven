# ─────────────────────────────────────────────────────────────────
# src/agent/base.py
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
from src.agent.models import AgentTask, AgentResult, AgentState

class BaseAgent(ABC):
    """
    Abstract Base Class for all production agents.
    Enforces a strict execution contract ensuring that all agents
    receive standard inputs and emit structured results.
    """
    
    @abstractmethod
    def execute(self, task: AgentTask, state: AgentState) -> AgentResult:
        """
        Executes the agent's logic for a given task.
        Must return an AgentResult containing typed outputs and an AgentExecutionReport.
        """
        pass
