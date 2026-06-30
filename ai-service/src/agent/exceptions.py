# ─────────────────────────────────────────────────────────────────
# src/agent/exceptions.py
# ─────────────────────────────────────────────────────────────────

class AgentError(Exception):
    """Base exception for all agent failures."""
    pass

class RetryableAgentError(AgentError):
    """
    Exception raised when an agent fails due to a transient error
    (e.g., rate limits, network timeouts). The Orchestrator will
    retry these using exponential backoff.
    """
    pass

class TerminalAgentError(AgentError):
    """
    Exception raised when an agent fails due to an unrecoverable error
    (e.g., context window exceeded, severe schema validation failures).
    The Orchestrator immediately fails the task without retries.
    """
    pass
