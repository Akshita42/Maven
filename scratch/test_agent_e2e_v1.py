import json
import uuid
from pprint import pprint

from src.agent.constants import AgentType, AgentStatus
from src.agent.models import AgentState, AgentTask, AgentExecutionBudget, OrchestratorExecutionReport
from src.agent.orchestrator import AgentOrchestrator
from src.agent.registry import AgentRegistry
from src.agent.agents.planner import PlannerAgent
from src.agent.agents.research import ResearchAgent
from src.agent.agents.critic import CriticAgent
from src.agent.agents.explanation import ExplanationAgent

# 1. Setup mock for PipelineService to bypass actual network and logic
from src.agent.services.pipeline_service import PipelineService
from src.report.models import InvestmentReport, ExecutiveSummary, CompanyOverview, ReportMetadata, ReportStatus
from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.models import InvestmentIntelligence
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.critique.models import InvestmentCritique
from src.recommendation.models import InvestmentRecommendation
from src.recommendation.constants import InvestmentStance, ConvictionLevel, TimeHorizon

def mock_run_from_query(query: str) -> InvestmentReport:
    print(f"   [PipelineService Mock] Running deterministic pipeline for: {query}")
    return InvestmentReport.model_construct(
        reportId=str(uuid.uuid4()),
        companyOverview=CompanyOverview.model_construct(ticker=query, companyName=f"{query} Inc"),
        executiveSummary=ExecutiveSummary.model_construct(stance=InvestmentStance.BUY, conviction=ConvictionLevel.HIGH, horizon=TimeHorizon.LONG_TERM, overallScore=8.5),
        evidence=EvidencePackage.model_construct(evidenceId="evi-1"),
        intelligence=InvestmentIntelligence.model_construct(intelligenceId="int-1"),
        thesis=InvestmentThesis.model_construct(thesisId="the-1"),
        committee=InvestmentCommitteeReview.model_construct(committeeId="com-1"),
        critique=InvestmentCritique.model_construct(
            critiqueId="cri-1",
            robustnessSummary={"stabilityIndex": 0.85, "assumptionQuality": 0.9}
        ),
        recommendation=InvestmentRecommendation.model_construct(recommendationId="rec-1"),
        meta=ReportMetadata.model_construct(status=ReportStatus.SUCCESS, compiledAt="2026-01-01T00:00:00Z")
    )

PipelineService.run_from_query = mock_run_from_query

def test_agent_e2e():
    print("================ TEST: AGENT END-TO-END ORCHESTRATION ================")
    
    # 2. Setup Registry & Agents
    registry = AgentRegistry()
    registry.register(AgentType.PLANNER, PlannerAgent())
    registry.register(AgentType.RESEARCH, ResearchAgent())
    registry.register(AgentType.CRITIC, CriticAgent())
    registry.register(AgentType.EXPLANATION, ExplanationAgent())
    
    orchestrator = AgentOrchestrator(registry)
    
    # 3. Simulate Session 1: Research Workflow
    print("\n--- User Input: 'Analyze Apple' ---")
    budget = AgentExecutionBudget()
    
    # Initially, we only push a PLANNER task to the queue
    initial_task = AgentTask(
        taskId="task-planner-1",
        agentType=AgentType.PLANNER,
        instruction="Analyze Apple",
        budget=budget
    )
    
    state = AgentState(
        sessionId="session-123",
        pendingTasks=[initial_task]
    )
    
    report1 = orchestrator.execute(state)
    
    print("\n--- Execution Report 1 ---")
    print(f"Overall Status: {report1.overallStatus}")
    print(f"Tasks Completed: {report1.completedTaskCount}")
    print("Events:")
    for event in report1.events:
        print(f" - {event.taskId} ({event.agentType}): {event.status}")
        
    print(f"\nWorkflow Metadata Populated:")
    print(f" Workflow Type: {state.memory.get('workflowType')}")
    print(f" Original Intent: {state.memory.get('originalUserIntent')}")
    
    # 4. Simulate Session 2: Explanation Workflow
    print("\n--- User Input: 'Why buy?' ---")
    
    followup_task = AgentTask(
        taskId="task-planner-2",
        agentType=AgentType.PLANNER,
        instruction="Why buy?",
        budget=budget
    )
    
    state.pendingTasks.append(followup_task)
    report2 = orchestrator.execute(state)
    
    print("\n--- Execution Report 2 ---")
    print(f"Overall Status: {report2.overallStatus}")
    print(f"Tasks Completed: {report2.completedTaskCount}")
    print("Events:")
    for event in report2.events:
        print(f" - {event.taskId} ({event.agentType}): {event.status}")
        
    # Check Explanation output
    # The last completed task should be the Explanation agent
    explain_result = state.completedTasks[-1]
    print(f"\nExplanation Agent Answer: {explain_result.output.get('answer')}")
    
    # Assertions
    assert report1.failedTaskCount == 0
    assert report2.failedTaskCount == 0
    assert state.memory.get("workflowType") == "EXPLANATION"
    assert "Why buy?" in state.memory.get("originalUserIntent")
    assert "rec-1" in explain_result.output.get("answer")
    assert len(state.pendingTasks) == 0
    
    print("\n✓ E2E Agent Architecture verified successfully.")

if __name__ == "__main__":
    test_agent_e2e()
