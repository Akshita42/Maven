# ─────────────────────────────────────────────────────────────────
# src/agent/agents/explanation.py
# ─────────────────────────────────────────────────────────────────

import time
import json
from src.agent.base import BaseAgent
from src.agent.constants import AgentStatus
from src.agent.models import AgentTask, AgentResult, AgentState, AgentExecutionReport
from src.agent.exceptions import TerminalAgentError
from src.report.service import ReportService
from src.infrastructure.llm.gemini_service import GeminiService

class ExplanationAgent(BaseAgent):
    """
    Answers user questions strictly from the generated InvestmentReport and lineage.
    Never invents reasoning or uses external knowledge.
    """
    
    def execute(self, task: AgentTask, state: AgentState) -> AgentResult:
        start_time = time.time()
        
        base_report_id = state.conversationContext.reportId if state.conversationContext else None
        base_report = ReportService.get(base_report_id) if base_report_id else None
        
        current_report = state.memory.get("current_report")
        
        reports_to_include = []
        if base_report:
            reports_to_include.append(base_report)
            
        if current_report and (not base_report or current_report.get("reportId") != base_report.get("reportId")):
            reports_to_include.append(current_report)
            
        if not reports_to_include:
            report_data = ReportService.get_latest(state.sessionId)
            if report_data:
                reports_to_include.append(report_data)

        if not reports_to_include:
            # Cannot answer if there is no report
            answer = "I cannot answer this because no stored report was found for this session."
            tokens_used = 0
            cost = 0.0
        else:
            explainability_level = state.conversationContext.explainabilityLevel if state.conversationContext else "Intermediate"
            
            # Build conversation history context
            history_str = ""
            if state.conversationContext and state.conversationContext.messages:
                # Include last 4 messages for context (excluding the current one)
                recent_msgs = state.conversationContext.messages[-5:-1] if len(state.conversationContext.messages) > 1 else []
                if recent_msgs:
                    history_str = "\nRecent Conversation History:\n"
                    for m in recent_msgs:
                        role = m.get("role", "unknown").upper()
                        content = m.get("content", "")
                        if content:
                            history_str += f"{role}: {content}\n"
                            
            reports_context = ""
            for report_data in reports_to_include:
                company = report_data.get("companyOverview", {}).get("companyName", "Unknown")
                
                thesis_statements = []
                if "thesis" in report_data and "sections" in report_data["thesis"]:
                    for sec in report_data["thesis"]["sections"].values():
                        if "statements" in sec:
                            for stmt in sec["statements"]:
                                thesis_statements.append(stmt.get("finding", ""))
                
                critique_vulns = []
                if "critique" in report_data and "actionableVulnerabilities" in report_data["critique"]:
                    vulns = report_data["critique"]["actionableVulnerabilities"].get("invalidatingAssumptions", [])
                    for v in vulns:
                        critique_vulns.append(v.get("description", ""))
                        
                reports_context += f"--- Report Context for {company} ---\n"
                reports_context += f"Recommendation: {json.dumps(report_data.get('recommendation', {}).get('stance'))}\n"
                reports_context += f"Key Positives: {json.dumps(report_data.get('recommendation', {}).get('keyPositives', [])[:3])}\n"
                reports_context += f"Key Risks: {json.dumps(report_data.get('recommendation', {}).get('keyRisks', [])[:3])}\n"
                reports_context += f"Thesis Statements: {json.dumps(thesis_statements)}\n"
                reports_context += f"Critical Vulnerabilities: {json.dumps(critique_vulns)}\n\n"
            
            prompt = f"""
You are Maven, a conversational AI investment copilot.
Your job is to answer the user's follow-up question naturally, acting as a helpful analyst. 
You must ONLY base your answers on the provided report context. Do NOT invent information.
Do NOT output raw data like "(Citation: Recommendation ID ...)" or system IDs. Speak naturally.
Keep your answer concise, confident, and direct.

Explainability Level Selected by User: {explainability_level}
{history_str}
User Query: "{task.instruction}"

{reports_context}

Answer the user's query naturally based on this context.
"""
            llm_service = GeminiService()
            try:
                # We separate system and user prompts for the text response method
                system_prompt = "You are Maven, a conversational AI investment copilot. Keep answers concise, confident, and direct."
                answer = llm_service.generate_text_response(system_prompt=system_prompt, user_prompt=prompt)
                tokens_used = llm_service.last_tokens_used or 0
                cost = (tokens_used / 1000) * 0.001
            except Exception as e:
                # Deterministic fallback on API failure (429, 503, timeout, etc.)
                company = reports_to_include[0].get("companyOverview", {}).get("companyName", "this company")
                stance = reports_to_include[0].get("recommendation", {}).get("stance", "HOLD")
                
                answer = (
                    f"This explanation is unavailable because an AI synthesis was unavailable. "
                    f"However, based on the completed deterministic report for {company}, my recommendation remains a **{stance}**."
                )
                tokens_used = 0
                cost = 0.0
                
        latency = (time.time() - start_time) * 1000
        
        exec_report = AgentExecutionReport(
            agentId="explanation-v1",
            agentVersion="1.0.0",
            status=AgentStatus.SUCCESS,
            latencyMs=latency,
            retryCount=0,
            tokensUsed=tokens_used,
            estimatedCostUsd=cost,
            toolsUsed=[],
            warnings=[]
        )
        
        return AgentResult(
            taskId=task.taskId,
            output={"answer": answer},
            report=exec_report
        )
