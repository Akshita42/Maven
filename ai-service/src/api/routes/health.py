# ─────────────────────────────────────────────────────────────────
# src/api/routes/health.py
# ─────────────────────────────────────────────────────────────────
#
# Route definitions for health checking.
# Maps GET /health to the health controller function.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.services.health_service import get_health_status
from src.utils.response import send_success

router = APIRouter()

@router.get("")
def health():
    """
    GET /health
    Returns service name, version, status, and uptime.
    This route is unauthenticated and used for container orchestrator checks.
    """
    health_data = get_health_status()
    return send_success(data=health_data)
