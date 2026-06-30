# ─────────────────────────────────────────────────────────────────
# src/agent/orchestrator.py
# ─────────────────────────────────────────────────────────────────

import time
import uuid
from datetime import datetime
from typing import Any
from src.agent.models import (
    AgentState, AgentTask, AgentResult, AgentExecutionReport,
    OrchestratorExecutionReport, OrchestratorEvent
)
from src.agent.constants import AgentStatus
from src.agent.exceptions import RetryableAgentError, TerminalAgentError
from src.agent.registry import AgentRegistry

class AgentOrchestrator:
    """
    Manages scheduling, retries, cancellation, and execution of agent tasks.
    Routes tasks to actual agent logic via AgentRegistry based on AgentType.
    Loops until pendingTasks is empty.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def start(self, instruction: str, context: 'ExecutionContext', state: AgentState) -> OrchestratorExecutionReport:
        """
        Initializes the workflow with a PlannerAgent task and begins execution.
        """
        from src.agent.models import AgentTask, AgentExecutionBudget
        from src.agent.constants import AgentType
        import uuid
        
        # Inject context into memory so sub-agents can extract it
        state.memory["execution_context"] = context
        
        initial_task = AgentTask(
            taskId=str(uuid.uuid4()),
            agentType=AgentType.PLANNER,
            instruction=instruction,
            budget=context.budget
        )
        state.pendingTasks.append(initial_task)
        print(f"Orchestrator started, appended PLANNER task. pendingTasks count: {len(state.pendingTasks)}")
        
        return self.execute(state, context)
        
    def execute(self, state: AgentState, context: 'ExecutionContext' = None) -> OrchestratorExecutionReport:
        start_time = time.time()
        events = []
        failed_count = 0
        completed_count = 0
        print(f"Orchestrator.execute starting. pendingTasks count: {len(state.pendingTasks)}")
        while state.pendingTasks:
            print(f"Looping pendingTasks... count: {len(state.pendingTasks)}")
            if context and context.cancellation_token.is_cancelled():
                events.append(OrchestratorEvent(
                    eventId=str(uuid.uuid4()),
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    taskId="SYSTEM",
                    agentType=AgentType.SYSTEM if hasattr(AgentType, "SYSTEM") else None,
                    status=AgentStatus.FAILED
                ))
                break
                
            task = state.pendingTasks.pop(0)
            task_start = time.time()
            retry_count = 0
            max_retries = 3
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    agent = self.registry.get_agent(task.agentType)
                    
                    print(f"Orchestrator: Executing task {task.agentType}")
                    result = agent.execute(task, state)
                    print(f"Orchestrator: Task {task.agentType} executed successfully")
                    
                    state.completedTasks.append(result)
                    
                    # If this was a planner task, it might have returned new tasks.
                    # We append them to the queue dynamically.
                    if task.agentType == task.agentType.PLANNER:
                        generated_tasks = result.output.get("generated_tasks", [])
                        for gt in generated_tasks:
                            # Convert dict back to AgentTask
                            new_task = AgentTask(**gt)
                            state.pendingTasks.append(new_task)
                            
                    events.append(OrchestratorEvent(
                        eventId=str(uuid.uuid4()),
                        timestamp=datetime.utcnow().isoformat() + "Z",
                        taskId=task.taskId,
                        agentType=task.agentType,
                        status=AgentStatus.SUCCESS
                    ))
                    
                    success = True
                    completed_count += 1
                    
                except RetryableAgentError as e:
                    print(f"ORCHESTRATOR RetryableAgentError: {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        events.append(self._create_fail_event(task))
                        failed_count += 1
                        break
                        
                except TerminalAgentError as e:
                    print(f"ORCHESTRATOR TerminalAgentError: {e}")
                    events.append(self._create_fail_event(task))
                    state.memory["workflow_error"] = str(e)
                    failed_count += 1
                    break
                    
                except Exception as e:
                    print(f"ORCHESTRATOR Exception: {e}")
                    import traceback
                    traceback.print_exc()
                    # Treat unexpected errors as terminal
                    events.append(self._create_fail_event(task))
                    failed_count += 1
                    break
                    
        total_latency = (time.time() - start_time) * 1000
        overall_status = AgentStatus.SUCCESS if failed_count == 0 else AgentStatus.FAILED
        
        return OrchestratorExecutionReport(
            overallStatus=overall_status,
            overallLatencyMs=total_latency,
            completedTaskCount=completed_count,
            failedTaskCount=failed_count,
            events=events
        )
        
    def _create_fail_event(self, task: AgentTask) -> OrchestratorEvent:
        return OrchestratorEvent(
            eventId=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            taskId=task.taskId,
            agentType=task.agentType,
            status=AgentStatus.FAILED
        )
