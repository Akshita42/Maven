import os
import sys
import time
import asyncio
from dotenv import load_dotenv

# Set dev env to trigger timings if there was any specific env check
os.environ["ENV"] = "development"

# Ensure we're in the right directory to import
sys.path.insert(0, r"c:\Projects\Maven\ai-service")

# Setup dummy observer and context
class DummyObserver:
    def on_event(self, event):
        pass

class DummyToken:
    def is_cancelled(self):
        return False

from src.agent.models import AgentExecutionBudget

class DummyContext:
    def __init__(self):
        self.observer = DummyObserver()
        self.cancellation_token = DummyToken()
        self.budget = AgentExecutionBudget(tokenLimit=100000, timeLimitMs=60000)

from src.agent.registry import AgentRegistry
from src.agent.orchestrator import AgentOrchestrator
from src.agent.models import AgentState
from src.agent.agents.planner import PlannerAgent
from src.agent.agents.research import ResearchAgent
from src.agent.agents.explanation import ExplanationAgent
from src.agent.constants import AgentType

def get_registry():
    r = AgentRegistry()
    r.register(AgentType.PLANNER, PlannerAgent())
    r.register(AgentType.RESEARCH, ResearchAgent())
    r.register(AgentType.EXPLANATION, ExplanationAgent())
    return r

def run_analysis():
    print("=== RUNNING ANALYSIS ===")
    registry = get_registry()
    orchestrator = AgentOrchestrator(registry)
    context = DummyContext()
    state = AgentState(
        sessionId="test-123",
        query="Analyze TSLA",
        pendingTasks=[],
        completedTasks=[],
        memory={}
    )
    # This will trigger PLANNER, which routes to RESEARCH, which runs the pipeline
    orchestrator.start("Analyze TSLA", context, state)

def run_explanation():
    print("\n=== RUNNING EXPLANATION ===")
    registry = get_registry()
    orchestrator = AgentOrchestrator(registry)
    context = DummyContext()
    state = AgentState(
        sessionId="test-123",
        query="What if Tesla margins drop?",
        pendingTasks=[],
        completedTasks=[],
        memory={}
    )
    # This will trigger PLANNER, which routes to EXPLANATION
    orchestrator.start("What if Tesla margins drop?", context, state)

if __name__ == "__main__":
    load_dotenv(r"c:\Projects\Maven\ai-service\.env")
    run_analysis()
    run_explanation()
