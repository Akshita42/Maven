# ─────────────────────────────────────────────────────────────────
# src/constants/error_codes.py
# ─────────────────────────────────────────────────────────────────
#
# Stable error identifiers shared across the ecosystem.
# The React client branches on these codes rather than raw messages.
# ─────────────────────────────────────────────────────────────────

# Generic
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
ROUTE_NOT_FOUND = "ROUTE_NOT_FOUND"
VALIDATION_ERROR = "VALIDATION_ERROR"
CONFIG_INVALID = "CONFIG_INVALID"

# AI/Research Domain (Phase 2+)
AI_INFERENCE_ERROR = "AI_INFERENCE_ERROR"
EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
RESEARCH_FAILED = "RESEARCH_FAILED"
