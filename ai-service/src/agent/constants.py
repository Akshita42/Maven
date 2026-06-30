# ─────────────────────────────────────────────────────────────────
# src/agent/constants.py
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class AgentType(str, Enum):
    PLANNER = "PLANNER"
    RESEARCH = "RESEARCH"
    CRITIC = "CRITIC"
    EXPLANATION = "EXPLANATION"

class AgentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
