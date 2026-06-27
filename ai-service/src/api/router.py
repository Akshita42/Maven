# ─────────────────────────────────────────────────────────────────
# src/api/router.py
# ─────────────────────────────────────────────────────────────────
#
# Main API Router.
# Mounts all sub-routers (route groups) under their namespaces.
# Keeps main.py clean as routes expand.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from src.api.routes.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

# Mount the health routes.
# Path resolves to: GET /api/v1/health
api_router.include_router(health_router, prefix="/health", tags=["health"])
