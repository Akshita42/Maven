import asyncio
from src.agent.agents.explanation import ExplanationAgent
from src.agent.models import AgentTask, AgentState, ConversationContext, AgentExecutionBudget
from src.agent.constants import AgentType
from src.report.service import ReportService
import glob
import os

async def test_expl():
    agent = ExplanationAgent()
    
    # 1. Pick the first report in the dir
    files = glob.glob(".data/reports/*.json")
    if not files:
        print("No reports!")
        return
        
    report_id = os.path.basename(files[0]).replace(".json", "")
    print("Using report:", report_id)
    
    report = ReportService.get(report_id)
    if not report:
        print("ReportService.get failed!")
        return
        
    sess_id = report.get("_sessionId", "test")
    
    state = AgentState(
        sessionId=sess_id,
        conversationContext=ConversationContext(
            sessionId=sess_id,
            reportId=report_id,
            currentCompany="Apple Inc.",
            messages=[],
            explainabilityLevel="Intermediate"
        ),
        memory={}
    )
    
    task = AgentTask(
        taskId="t1",
        agentType=AgentType.EXPLANATION,
        instruction="Why hold?",
        budget=AgentExecutionBudget()
    )
    
    res = agent.execute(task, state)
    print("Result:", res.output)

if __name__ == "__main__":
    asyncio.run(test_expl())
