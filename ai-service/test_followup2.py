import asyncio
from src.agent.orchestrator import AgentOrchestrator
from src.agent.registry import AgentRegistry
from src.core.execution_context import ExecutionContext, CancellationToken
from src.agent.models import AgentState, ConversationContext, AgentExecutionBudget
from src.api.adapters.sse_adapter import SSEEventAdapter
import uuid

async def main():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)
    
    session_id = "test-session"
    
    queue = asyncio.Queue()
    cancel_token = CancellationToken()
    observer = SSEEventAdapter(queue, asyncio.get_running_loop(), session_id, "req-1", "wf-1")
    context = ExecutionContext(
        request_id="req-1",
        workflow_id="wf-1",
        session_id=session_id,
        observer=observer,
        logger=None,
        budget=AgentExecutionBudget(),
        cancellation_token=cancel_token
    )
    
    # 1. Generate report
    state1 = AgentState(
        sessionId=session_id,
        conversationContext=ConversationContext(
            sessionId=session_id,
            reportId=None,
            currentCompany=None,
            messages=[],
            explainabilityLevel="Intermediate"
        ),
        memory={}
    )
    
    print("=== ANALYSIS ===")
    report1 = orchestrator.start("Analyze Apple", context, state1)
    
    # extract reportId
    rep = state1.memory.get("current_report")
    if not rep:
        print("NO REPORT GENERATED")
        return
        
    report_id = rep.get("reportId")
    print("Report ID:", report_id)
    
    # save report as chat.py does
    from src.report.service import ReportService
    ReportService.save(rep, session_id)
    print("Saved!")
    
    # 2. Follow up
    state2 = AgentState(
        sessionId=session_id,
        conversationContext=ConversationContext(
            sessionId=session_id,
            reportId=report_id,
            currentCompany="Apple Inc.",
            messages=[],
            explainabilityLevel="Intermediate"
        ),
        memory={
            "reportId": report_id,
            "currentCompany": "Apple Inc."
        }
    )
    
    print("=== EXPLANATION ===")
    report2 = orchestrator.start("Why hold?", context, state2)
    
    for t in state2.completedTasks:
        print(t.agentType, t.output)
        
if __name__ == "__main__":
    asyncio.run(main())
