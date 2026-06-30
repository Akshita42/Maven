import asyncio
import json
import uuid
import sys
import os

# Add to Python path
sys.path.append("c:/Projects/Maven/ai-service")

from src.application.bootstrap import get_orchestrator
from src.core.execution_context import ExecutionContext, CancellationToken
from src.agent.models import AgentState, AgentExecutionBudget, ConversationContext

class MockObserver:
    def on_event(self, event):
        print(f"EVENT: {event.model_dump_json(indent=2)}")

async def run_test():
    orchestrator = get_orchestrator()
    session_id = str(uuid.uuid4())
    context = ExecutionContext(
        request_id=str(uuid.uuid4()),
        workflow_id=str(uuid.uuid4()),
        session_id=session_id,
        observer=MockObserver(),
        logger=None,
        budget=AgentExecutionBudget(),
        cancellation_token=CancellationToken()
    )
    
    state = AgentState(
        sessionId=session_id,
        conversationContext=ConversationContext(
            sessionId=session_id,
        )
    )
    
    print("Running orchestrator for 'Analyze Apple'")
    result = await asyncio.to_thread(orchestrator.start, "Analyze Apple", context, state)
    print("Orchestrator finished.")
    
    if "current_report" in state.memory:
        report = state.memory["current_report"]
        print(f"Generated report for {report.get('companyOverview', {}).get('companyName')}")
        
        # Test ReportService
        from src.report.service import ReportService
        ReportService.save(report, session_id)
        
        saved = ReportService.get(report["reportId"])
        if saved:
            print(f"Successfully verified persistence! Report ID: {saved['reportId']}")
        else:
            print("Persistence verification failed!")
    else:
        print("No report was generated.")

if __name__ == "__main__":
    asyncio.run(run_test())
