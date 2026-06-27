# ─────────────────────────────────────────────────────────────────
# src/constants/api.py
# ─────────────────────────────────────────────────────────────────
#
# Central registry for API constants and configuration mappings.
# Prevents magic strings from leaking into route and response logic.
# ─────────────────────────────────────────────────────────────────

SERVICE_NAME = "maven-ai-service"
VERSION = "1.0.0"

# Response Status Envelopes
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# Health States
HEALTH_HEALTHY = "healthy"
HEALTH_DEGRADED = "degraded"
HEALTH_UNHEALTHY = "unhealthy"

# External APIs
YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
