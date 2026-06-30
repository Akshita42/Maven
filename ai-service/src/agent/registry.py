# ─────────────────────────────────────────────────────────────────
# src/agent/registry.py
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Type
from src.agent.constants import AgentType
from src.agent.base import BaseAgent
from src.agent.exceptions import TerminalAgentError

class AgentRegistry:
    """
    Central registry for resolving concrete agent instances by AgentType.
    Allows the AgentOrchestrator to remain decoupled from agent implementations.
    """
    
    def __init__(self):
        self._agents: Dict[AgentType, BaseAgent] = {}
        
    def register(self, agent_type: AgentType, agent: BaseAgent) -> None:
        """Registers a concrete agent implementation."""
        self._agents[agent_type] = agent
        
    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        """Resolves an agent by type. Raises TerminalAgentError if not found."""
        agent = self._agents.get(agent_type)
        if not agent:
            raise TerminalAgentError(f"No agent registered for type: {agent_type}")
        return agent
