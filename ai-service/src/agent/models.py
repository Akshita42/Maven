# ─────────────────────────────────────────────────────────────────
# src/agent/models.py
# ─────────────────────────────────────────────────────────────────

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from src.agent.constants import AgentType, AgentStatus

class AgentExecutionBudget(BaseModel):
    """Enforces strict bounds per agent task execution."""
    model_config = ConfigDict(frozen=True)
    
    timeoutMs: int = 30000
    maxTokens: int = 4096
    maxCostUsd: float = 1.0

class AgentExecutionReport(BaseModel):
    """Deterministic telemetry for an executed task."""
    model_config = ConfigDict(frozen=True)
    
    agentId: str
    agentVersion: str
    status: AgentStatus
    latencyMs: float
    retryCount: int
    tokensUsed: int
    estimatedCostUsd: float
    toolsUsed: List[str]
    warnings: List[str]

class AgentTask(BaseModel):
    """Immutable contract defining a specific goal and output schema."""
    model_config = ConfigDict(frozen=True)
    
    taskId: str
    agentType: AgentType
    instruction: str
    budget: AgentExecutionBudget

class AgentResult(BaseModel):
    """Immutable contract returning the typed output of a completed task."""
    model_config = ConfigDict(frozen=True)
    
    taskId: str
    output: Dict[str, Any]
    report: AgentExecutionReport

class Recommendation(BaseModel):
    action: str = Field(..., description="Must be BUY, HOLD, or SELL for downstream compatibility")
    investmentOutlook: str = Field(..., description="Overall outlook: Bullish, Neutral, or Bearish")
    suggestedActions: List[str] = Field(..., description="Context-aware actions. e.g. 'New Investor -> BUY', 'Existing Holder -> HOLD'")
    confidenceScore: float = Field(..., description="0.0 to 1.0 confidence in the recommendation")
    horizon: str = Field(..., description="e.g., SHORT_TERM, MEDIUM_TERM, LONG_TERM")
    keyPositives: List[str] = Field(..., description="Human-readable business positive points")
    keyRisks: List[str] = Field(..., description="Human-readable fundamental business risks")
    explainabilityLevel: str = "intermediate"

class ConversationContext(BaseModel):
    """Immutable context reflecting the conversational state of the user session."""
    model_config = ConfigDict(frozen=True)

    sessionId: str
    reportId: Optional[str] = None
    currentCompany: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    explainabilityLevel: str = "intermediate"

class AgentState(BaseModel):
    """Global framework-agnostic state object passed sequentially between steps."""
    model_config = ConfigDict(frozen=False)
    
    sessionId: str
    conversationContext: Optional[ConversationContext] = None
    completedTasks: List[AgentResult] = Field(default_factory=list)
    pendingTasks: List[AgentTask] = Field(default_factory=list)
    memory: Dict[str, Any] = Field(default_factory=dict)

class OrchestratorEvent(BaseModel):
    """Event log for a single task orchestration step."""
    model_config = ConfigDict(frozen=True)
    
    eventId: str
    timestamp: str
    taskId: str
    agentType: AgentType
    status: AgentStatus

class OrchestratorExecutionReport(BaseModel):
    """Execution observability for the entire orchestration layer run."""
    model_config = ConfigDict(frozen=True)
    
    overallStatus: AgentStatus
    overallLatencyMs: float
    completedTaskCount: int
    failedTaskCount: int
    events: List[OrchestratorEvent]
