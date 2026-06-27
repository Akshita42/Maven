# ─────────────────────────────────────────────────────────────────
# src/services/health_service.py
# ─────────────────────────────────────────────────────────────────
#
# Business logic for health checking.
# Calculates process uptime and returns service status.
# ─────────────────────────────────────────────────────────────────

import time
from datetime import datetime
from src.constants.api import SERVICE_NAME, VERSION, HEALTH_HEALTHY

# Record start time at module load (application startup)
START_TIME = time.time()

def get_health_status() -> dict:
    """
    Calculates process uptime and returns a health status payload.
    
    Uptime is calculated relative to START_TIME.
    Timestamp is returned in ISO 8601 format.
    """
    uptime_seconds = time.time() - START_TIME
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "status": HEALTH_HEALTHY,
        "uptime": round(uptime_seconds, 3),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
