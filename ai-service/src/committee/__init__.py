# ─────────────────────────────────────────────────────────────────
# src/committee/__init__.py
# ─────────────────────────────────────────────────────────────────
#
# Module initialization registering built-in production reviewers.
# ─────────────────────────────────────────────────────────────────

from src.committee.registry import ReviewerRegistry
from src.committee.reviewers.business import BusinessReviewer
from src.committee.reviewers.financial import FinancialReviewer
from src.committee.reviewers.valuation import ValuationReviewer
from src.committee.reviewers.risk import RiskReviewer
from src.committee.reviewers.governance import GovernanceReviewer

# Register production built-in reviewers automatically.
# Uses try-except to prevent errors during hot reloads or test overrides.
try:
    ReviewerRegistry.register(BusinessReviewer())
    ReviewerRegistry.register(FinancialReviewer())
    ReviewerRegistry.register(ValuationReviewer())
    ReviewerRegistry.register(RiskReviewer())
    ReviewerRegistry.register(GovernanceReviewer())
except ValueError:
    pass
