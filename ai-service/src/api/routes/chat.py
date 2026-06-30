# ─────────────────────────────────────────────────────────────────
# src/api/routes/chat.py
# ─────────────────────────────────────────────────────────────────
#
# Route definitions for streaming chat interaction via SSE.
# ─────────────────────────────────────────────────────────────────

import json
import uuid
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.core.execution_context import ExecutionContext, CancellationToken
from src.api.adapters.sse_adapter import SSEEventAdapter
from src.agent.models import AgentState, AgentExecutionBudget
from src.application.bootstrap import get_orchestrator

router = APIRouter()
orchestrator = get_orchestrator()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatStreamRequest(BaseModel):
    query: str
    sessionId: str
    reportId: Optional[str] = None
    history: List[ChatMessage] = []
    currentCompany: Optional[str] = None
    explainabilityLevel: Optional[str] = "Intermediate"

async def event_generator(queue: asyncio.Queue, cancel_token: CancellationToken, request: Request):
    print("ENTER chat.py event_generator")
    try:
        while True:
            # Wait for the next SSE payload from the observer queue
            print("event_generator: waiting for queue.get()")
            event_data = await queue.get()
            print(f"event_generator: dequeued event: {event_data.get('type') if isinstance(event_data, dict) else 'unknown'}")
            
            # Check for termination BEFORE yielding
            # In SSE, we want to yield the terminal event so the client sees it,
            # then we break the generator loop to close the HTTP stream.
            if event_data.get("type") in ("completed", "error"):
                if event_data.get("type") == "error":
                    err_msg = event_data.get("error", "")
                    
                    if "I found multiple companies matching" in err_msg:
                        clean_msg = err_msg[err_msg.find("I found multiple companies matching"):]
                    elif "No public company found" in err_msg:
                        clean_msg = f"I couldn't find a publicly traded stock for this search. It might be a private company, an acquired company, or not listed on supported exchanges. If you're sure it's public, please specify the exact ticker symbol."
                    else:
                        clean_msg = "I temporarily couldn't complete the analysis due to an internal issue. Please try again in a few moments."
                        
                    mock_completed = {
                        "type": "completed",
                        "report_id": "",
                        "report_data": None,
                        "content": clean_msg
                    }
                    yield f"data: {json.dumps(mock_completed)}\n\n"
                    print("event_generator: error intercepted, terminal event yielded, breaking loop")
                    break
                    
                yield f"data: {json.dumps(event_data)}\n\n"
                print("event_generator: terminal event yielded, breaking loop")
                break
                
            yield f"data: {json.dumps(event_data)}\n\n"
            
    except asyncio.CancelledError:
        # The client disconnected prematurely
        print("event_generator: client disconnected")
        cancel_token.cancel()
        raise
    except Exception as e:
        print(f"event_generator exception: {e}")
        yield f"data: {json.dumps({'type': 'error', 'error': 'Internal server error during streaming'})}\n\n"
    finally:
        print("EXIT chat.py event_generator")

@router.post("/stream")
async def chat_stream(payload: ChatStreamRequest, request: Request):
    """
    POST /api/v1/chat/stream
    """
    print("ENTER chat endpoint")
    request_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()
    print("CREATE queue")
    
    cancel_token = CancellationToken()
    observer = SSEEventAdapter(
        queue=queue, 
        loop=loop,
        session_id=payload.sessionId,
        request_id=request_id,
        workflow_id=workflow_id
    )
    print("CREATE observer")
    
    budget = AgentExecutionBudget()
    context = ExecutionContext(
        request_id=request_id,
        workflow_id=workflow_id,
        session_id=payload.sessionId,
        observer=observer,
        logger=None, 
        budget=budget,
        cancellation_token=cancel_token
    )
    
    # Enrich context
    current_company = payload.currentCompany
    if payload.reportId and not current_company:
        from src.report.service import ReportService
        existing_report = ReportService.get(payload.reportId)
        if existing_report and "companyOverview" in existing_report:
            current_company = existing_report["companyOverview"].get("companyName")

    from src.agent.models import ConversationContext
    state = AgentState(
        sessionId=payload.sessionId,
        conversationContext=ConversationContext(
            sessionId=payload.sessionId,
            reportId=payload.reportId,
            currentCompany=current_company,
            messages=[msg.model_dump() for msg in payload.history],
            explainabilityLevel=payload.explainabilityLevel or "Intermediate"
        ),
        memory={
            "reportId": payload.reportId,
            "currentCompany": current_company,
            "conversationHistory": [msg.model_dump() for msg in payload.history]
        }
    )
    
    async def run_orchestrator():
        try:
            print("START orchestrator task")
            await asyncio.to_thread(orchestrator.start, payload.query, context, state)
            print("WORKFLOW finished")
            if not cancel_token.is_cancelled():
                workflow_type = state.memory.get("workflowType", "UNKNOWN")
                
                if workflow_type in ["EXPLANATION", "CHALLENGE", "COMPARE"]:
                    answer = "No response generated."
                    if state.completedTasks:
                        answer = state.completedTasks[-1].output.get("answer", answer)
                        
                    from src.core.events import WorkflowCompleted
                    from src.report.service import ReportService
                    
                    existing_report = {}
                    if payload.reportId:
                        existing_report = {"reportId": payload.reportId}
                        
                    evt = WorkflowCompleted(report_id=payload.reportId or "", report_data=existing_report)
                    evt.content = answer
                    observer.on_event(evt)
                    
                else:
                    report_data = state.memory.get("current_report")
                    if report_data:
                        from src.report.service import ReportService
                        try:
                            ReportService.save(report_data, payload.sessionId)
                            report_id = report_data.get("reportId", "")
                            
                            # VERIFY PERSISTENCE
                            persisted_report = ReportService.get(report_id)
                            if not persisted_report:
                                raise Exception(f"Report {report_id} saved but immediately unavailable during retrieval.")
                                
                            # Generate deterministic conversational summary
                            company_name = persisted_report.get("companyOverview", {}).get("companyName", "the company")
                            stance = persisted_report.get("recommendation", {}).get("stance", "HOLD").replace("_", " ")
                            positives = persisted_report.get("recommendation", {}).get("keyPositives", [])
                            risks = persisted_report.get("recommendation", {}).get("keyRisks", [])
                            
                            def lower_first(s):
                                return s[:1].lower() + s[1:] if s else s
                                
                            top_positives = [lower_first(p) for p in positives[:3]] if positives else ["its overall fundamentals"]
                            if len(top_positives) > 1:
                                positives_str = ", ".join(top_positives[:-1]) + f", and {top_positives[-1]}"
                            else:
                                positives_str = top_positives[0]
                                
                            primary_risk = lower_first(risks[0]) if risks else "broader market conditions"
                            
                            natural_response = (
                                f"I finished analyzing {company_name}. Based on the available evidence, I currently recommend **{stance}**.\n\n"
                                f"The strongest reasons are {positives_str}. The biggest concern is {primary_risk}.\n\n"
                                f"You can ask me to explain any part of this recommendation or challenge my reasoning."
                            )
                                
                            from src.core.events import WorkflowCompleted
                            evt = WorkflowCompleted(report_id=report_id, report_data=persisted_report)
                            evt.content = natural_response
                            observer.on_event(evt)
                        except Exception as e:
                            print(f"ERROR saving report: {e}")
                            from src.core.events import WorkflowFailed
                            observer.on_event(WorkflowFailed(stage="orchestration", error=f"Workflow failed internally. Persistence error: {str(e)}"))
                    else:
                        print("ERROR: Orchestrator finished without generating a report.")
                        from src.core.events import WorkflowFailed
                        error_msg = state.memory.get("workflow_error", "Workflow failed internally. No report was generated.")
                        observer.on_event(WorkflowFailed(stage="orchestration", error=error_msg))
        except Exception as e:
            print(f"WORKFLOW exception: {e}")
            from src.core.events import WorkflowFailed
            observer.on_event(WorkflowFailed(stage="orchestration", error=str(e)))
            
    print("START orchestrator")
    asyncio.create_task(run_orchestrator())
    
    return StreamingResponse(
        event_generator(queue, cancel_token, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
