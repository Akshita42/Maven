import json
from pprint import pprint

from src.agent.constants import AgentType, AgentStatus
from src.agent.models import AgentState, AgentTask, AgentExecutionBudget, OrchestratorExecutionReport
from src.agent.orchestrator import AgentOrchestrator
from src.agent.exceptions import RetryableAgentError, TerminalAgentError
from src.agent.compiler import EvidenceCompiler

def mock_research_agent(task: AgentTask, state: AgentState):
    if "fail_retryable" in task.instruction:
        raise RetryableAgentError("Mock network timeout")
    if "fail_terminal" in task.instruction:
        raise TerminalAgentError("Mock context window exceeded")
        
    return {"data": "Mock research data"}

def mock_planner_agent(task: AgentTask, state: AgentState):
    return {"plan": ["task1", "task2"]}

def mock_critic_agent(task: AgentTask, state: AgentState):
    return {"feedback": "Looks good."}

def test_orchestration():
    print("================ TEST: AGENT ORCHESTRATOR ================")
    
    # 1. Setup routers
    routers = {
        AgentType.RESEARCH: mock_research_agent,
        AgentType.PLANNER: mock_planner_agent,
        AgentType.CRITIC: mock_critic_agent
    }
    
    orchestrator = AgentOrchestrator(routers)
    
    # 2. Setup state and tasks
    budget = AgentExecutionBudget()
    
    task1 = AgentTask(taskId="t1", agentType=AgentType.RESEARCH, instruction="Normal research", budget=budget)
    task2 = AgentTask(taskId="t2", agentType=AgentType.RESEARCH, instruction="fail_retryable", budget=budget)
    
    state = AgentState(
        sessionId="session-123",
        pendingTasks=[task1, task2]
    )
    
    print(f"Executing {len(state.pendingTasks)} tasks...")
    
    report = orchestrator.execute(state)
    
    print("\n--- Orchestrator Report ---")
    print(f"Overall Status: {report.overallStatus}")
    print(f"Completed Tasks: {report.completedTaskCount}")
    print(f"Failed Tasks: {report.failedTaskCount}")
    print("Events:")
    for event in report.events:
        print(f" - {event.taskId} ({event.agentType}): {event.status}")
        
    print("\n--- Final Agent State ---")
    print(f"Remaining Pending Tasks: {len(state.pendingTasks)}")
    print(f"Completed Tasks in State: {len(state.completedTasks)}")
    
    assert report.failedTaskCount == 1
    assert report.completedTaskCount == 1
    assert len(state.pendingTasks) == 1
    assert len(state.completedTasks) == 1
    
    print("\n✓ Orchestrator routing and error handling verified.")

if __name__ == "__main__":
    test_orchestration()
