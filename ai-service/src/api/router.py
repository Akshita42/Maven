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
from src.api.routes.company import router as company_router
from src.api.routes.evidence import router as evidence_router
from src.api.routes.intelligence import router as intelligence_router
from src.api.routes.thesis import router as thesis_router
from src.api.routes.committee import router as committee_router

api_router = APIRouter(prefix="/api/v1")

# Mount the health routes.
# Path resolves to: GET /api/v1/health
api_router.include_router(health_router, prefix="/health", tags=["health"])

# Mount the company routes.
# Path resolves to: POST /api/v1/company/resolve
api_router.include_router(company_router, prefix="/company", tags=["company"])

# Mount the evidence routes.
# Path resolves to: POST /api/v1/evidence/collect
api_router.include_router(evidence_router, prefix="/evidence", tags=["evidence"])

# Mount the intelligence routes.
# Path resolves to: POST /api/v1/intelligence/analyze
api_router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])

# Mount the thesis routes.
# Path resolves to: POST /api/v1/thesis/build
api_router.include_router(thesis_router, prefix="/thesis", tags=["thesis"])

# Mount the committee routes.
# Path resolves to: POST /api/v1/committee/review
api_router.include_router(committee_router, prefix="/committee", tags=["committee"])
