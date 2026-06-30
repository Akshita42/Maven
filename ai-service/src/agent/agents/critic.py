# ─────────────────────────────────────────────────────────────────
# src/agent/agents/critic.py
# ─────────────────────────────────────────────────────────────────

import time
from src.agent.base import BaseAgent
from src.agent.constants import AgentStatus
from src.agent.models import AgentTask, AgentResult, AgentState, AgentExecutionReport
from src.agent.exceptions import TerminalAgentError
from src.report.service import ReportService

class CriticAgent(BaseAgent):
    """
    Wraps the existing Phase 10 Self-Critique outputs present in the Report.
    Returns approval/review observations without modifying reports or adding
    new critique logic.
    """
    
    def execute(self, task: AgentTask, state: AgentState) -> AgentResult:
        start_time = time.time()
        
        report_id = state.conversationContext.reportId if state.conversationContext else state.memory.get("reportId")
        if report_id:
            report_data = ReportService.get(report_id)
        else:
            report_data = ReportService.get_latest(state.sessionId)

        if not report_data:
            raise TerminalAgentError("CriticAgent requires an InvestmentReport persisted in ReportRepository.")
            
        try:
            # Extract deterministic critique highlights from the report
            critique_data = report_data.get("critique", {})
            robustness = critique_data.get("robustnessSummary", {})
            
            observations = [
                f"Stability Index: {robustness.get('stabilityIndex', 'N/A')}",
                f"Assumption Quality: {robustness.get('assumptionQuality', 'N/A')}"
            ]
            
            latency = (time.time() - start_time) * 1000
            
            exec_report = AgentExecutionReport(
                agentId="critic-v1",
                agentVersion="1.0.0",
                status=AgentStatus.SUCCESS,
                latencyMs=latency,
                retryCount=0,
                tokensUsed=50,
                estimatedCostUsd=0.001,
                toolsUsed=[],
                warnings=[]
            )
            
            return AgentResult(
                taskId=task.taskId,
                output={"observations": observations},
                report=exec_report
            )
            
        except Exception as e:
            raise TerminalAgentError(f"CriticAgent failed to inspect report: {str(e)}")
