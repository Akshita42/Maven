# ─────────────────────────────────────────────────────────────────
# src/agent/agents/research.py
# ─────────────────────────────────────────────────────────────────

import time
from src.agent.base import BaseAgent
from src.agent.constants import AgentStatus
from src.agent.models import AgentTask, AgentResult, AgentState, AgentExecutionReport
from src.agent.services.pipeline_service import PipelineService
from src.agent.exceptions import TerminalAgentError

class ResearchAgent(BaseAgent):
    """
    Executes the real deterministic pipeline through the PipelineService façade.
    Never generates mock evidence except when patched in integration tests.
    """
    
    def execute(self, task: AgentTask, state: AgentState) -> AgentResult:
        start_time = time.time()
        
        try:
            # The Planner is assumed to pass the query via task instruction 
            # or state memory. For simplicity, we use task.instruction here.
            # E.g., "Analyze Apple" -> query "Apple"
            query = task.instruction.replace("Analyze ", "").strip()
            if not query:
                query = "UNKNOWN"
                
            context = state.memory.get("execution_context")
            if not context:
                raise TerminalAgentError("Execution context not found in AgentState memory.")
                
            report = PipelineService.run_from_query(query, context)
            
            # Persist report in state memory for subsequent agents
            state.memory["current_report"] = report.model_dump()
            
            latency = (time.time() - start_time) * 1000
            
            exec_report = AgentExecutionReport(
                agentId="research-v1",
                agentVersion="1.0.0",
                status=AgentStatus.SUCCESS,
                latencyMs=latency,
                retryCount=0,
                tokensUsed=500,
                estimatedCostUsd=0.01,
                toolsUsed=["PipelineService"],
                warnings=[]
            )
            
            return AgentResult(
                taskId=task.taskId,
                output={"status": "Report Generated", "reportId": report.reportId},
                report=exec_report
            )
            
        except Exception as e:
            raise TerminalAgentError(f"Research Agent failed to run pipeline: {str(e)}")
