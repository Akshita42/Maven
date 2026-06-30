from src.agent.registry import AgentRegistry
from src.agent.agents.planner import PlannerAgent
from src.agent.agents.research import ResearchAgent
from src.agent.agents.critic import CriticAgent
from src.agent.agents.explanation import ExplanationAgent
from src.agent.orchestrator import AgentOrchestrator
from src.agent.constants import AgentType

class ApplicationContainer:
    _instance = None
    
    def __init__(self):
        # Instantiate and wire the core dependencies exactly once
        self.registry = AgentRegistry()
        self.registry.register(AgentType.PLANNER, PlannerAgent())
        self.registry.register(AgentType.RESEARCH, ResearchAgent())
        self.registry.register(AgentType.CRITIC, CriticAgent())
        self.registry.register(AgentType.EXPLANATION, ExplanationAgent())
        
        self.orchestrator = AgentOrchestrator(self.registry)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

def get_orchestrator() -> AgentOrchestrator:
    return ApplicationContainer.get_instance().orchestrator
