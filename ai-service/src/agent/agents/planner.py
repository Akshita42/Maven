# ─────────────────────────────────────────────────────────────────
# src/agent/agents/planner.py
# ─────────────────────────────────────────────────────────────────

import time
import uuid
from datetime import datetime
from src.agent.base import BaseAgent
from src.agent.constants import AgentType, AgentStatus
from src.agent.models import AgentTask, AgentResult, AgentState, AgentExecutionReport, AgentExecutionBudget
from src.infrastructure.llm.gemini_service import GeminiService
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    workflowType: str = Field(..., description="Must be one of: ANALYSIS, EXPLANATION, CHALLENGE, COMPARE, OUT_OF_DOMAIN, UNKNOWN")
    targetCompany: str = Field(None, description="If workflowType is COMPARE or ANALYSIS, the name of the company to analyze.")

class PlannerAgent(BaseAgent):
    """
    Parses user intent and dynamically outputs AgentTasks to be executed by the Orchestrator.
    Populates lightweight planning metadata into AgentState for observability.
    Does NOT execute tasks or orchestrate.
    """
    
    def execute(self, task: AgentTask, state: AgentState) -> AgentResult:
        start_time = time.time()
        
        # 1. Update State Metadata
        state.memory["workflowId"] = str(uuid.uuid4())
        state.memory["createdAt"] = datetime.utcnow().isoformat() + "Z"
        state.memory["originalUserIntent"] = task.instruction
        
        # 2. Dynamic Routing Logic
        new_tasks = []
        budget = AgentExecutionBudget()
        
        report_id = state.conversationContext.reportId if state.conversationContext else state.memory.get("reportId")
        current_company = state.conversationContext.currentCompany if state.conversationContext else state.memory.get("currentCompany")
        history = state.conversationContext.messages if state.conversationContext else []
        history_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in history[-5:]]) # last 5 messages
        
        lower_instruction = task.instruction.lower().strip()
        workflow_type = None
        target_company_from_llm = None
        
        prompt = f"""
        You are an intent classifier for Maven, an AI Investment Research Copilot.
        Classify the following user instruction into one of these workflow types:
        - ANALYSIS: The user wants to start a new deep-dive financial analysis on a company. (e.g. 'Analyze Apple', 'Look up Google').
        - EXPLANATION: The user is asking a follow-up question about the CURRENT report, or a general finance/investing question.
        - CHALLENGE: The user wants to challenge, criticize, or counter the current recommendation.
        - COMPARE: The user wants to compare the CURRENT company with a DIFFERENT company.
        - OUT_OF_DOMAIN: Unrelated to finance, investing, companies, or the report.
        - UNKNOWN: None of the above.
        
        Context:
        - Current Company in focus: {current_company if current_company else 'None'}
        - Has active report: {bool(report_id)}
        - Recent Conversation History:
        {history_text}
        
        Crucial rules:
        - If the user uses pronouns like 'it', 'they', 'this company', or asks 'Should I invest in it?', 'Why?', 'What if revenue falls?', this MUST be classified as EXPLANATION because they are referring to the Current Company in focus. Do not classify as ANALYSIS.
        - If the previous message was asking the user to clarify an ambiguity (e.g. "Did you mean X or Y?"), and the user responds with a clarification (e.g. "the first one", "TCS.NS", "Tata"), you MUST classify as ANALYSIS. Extract ONLY the ticker symbol (e.g., 'TCS.NS', '0221.KL', 'AAPL') of the chosen company from the history into `targetCompany`. Do not include the full company name.
        - If they want to analyze a completely different company than the current one, it is ANALYSIS.
        - If the workflowType is COMPARE or ANALYSIS, extract the name or ticker of the new company into `targetCompany`.
        
        User Instruction: "{task.instruction}"
        """
        try:
            llm_service = GeminiService()
            response_text = llm_service.generate_json_response(
                system_prompt="You must respond in valid JSON format according to the schema: {'workflowType': 'ANALYSIS' | 'EXPLANATION' | 'CHALLENGE' | 'COMPARE' | 'OUT_OF_DOMAIN' | 'UNKNOWN', 'targetCompany': 'string (optional)'}",
                user_prompt=prompt
            )
            import json
            data = json.loads(response_text)
            workflow_type = data.get("workflowType", "UNKNOWN")
            target_company_from_llm = data.get("targetCompany")
        except Exception as e:
            # If LLM fails (e.g. 429 quota), we MUST propagate the error, not fallback to UNKNOWN/EXPLANATION
            from src.agent.exceptions import TerminalAgentError
            if isinstance(e, TerminalAgentError):
                raise
            print(f"Planner LLM Error: {e}")
            raise TerminalAgentError(f"Planner classification failed: {str(e)}")
        
        # Validate LLM output deterministically
        if workflow_type not in ["ANALYSIS", "EXPLANATION", "CHALLENGE", "COMPARE", "OUT_OF_DOMAIN"]:
            workflow_type = "UNKNOWN"
            
        print(f"PLANNER DEBUG - query: {task.instruction}, classified as: {workflow_type}")
            
        state.memory["workflowType"] = workflow_type
        
        if workflow_type == "ANALYSIS":
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.RESEARCH,
                instruction=target_company_from_llm if target_company_from_llm else task.instruction,
                budget=budget
            ))
        elif workflow_type == "COMPARE":
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.RESEARCH,
                instruction=target_company_from_llm if target_company_from_llm else task.instruction,
                budget=budget
            ))
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.EXPLANATION,
                instruction=task.instruction,
                budget=budget
            ))
        elif workflow_type == "CHALLENGE":
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.EXPLANATION,
                instruction=task.instruction,
                budget=budget
            ))
        elif workflow_type == "EXPLANATION":
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.EXPLANATION,
                instruction=task.instruction,
                budget=budget
            ))
        elif workflow_type == "OUT_OF_DOMAIN":
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.EXPLANATION,
                instruction="The user asked an out-of-domain question. Politely decline and state that you are an AI Investment Copilot focused on financial research and cannot answer this.",
                budget=budget
            ))
        else:
            new_tasks.append(AgentTask(
                taskId=str(uuid.uuid4()),
                agentType=AgentType.EXPLANATION,
                instruction="Unknown intent. Please clarify your request.",
                budget=budget
            ))
            
        latency = (time.time() - start_time) * 1000
        
        report = AgentExecutionReport(
            agentId="planner-v1",
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
            output={"generated_tasks": [t.model_dump() for t in new_tasks]},
            report=report
        )
