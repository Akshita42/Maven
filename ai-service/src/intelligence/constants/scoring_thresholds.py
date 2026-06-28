# ─────────────────────────────────────────────────────────────────
# src/intelligence/constants/scoring_thresholds.py
# ─────────────────────────────────────────────────────────────────
#
# Centrally managed scoring thresholds and weights.
# ─────────────────────────────────────────────────────────────────

# ── Pillar Weights Configuration ──
PILLAR_WEIGHTS = {
    "business_quality": 0.20,
    "financial_health": 0.30,
    "growth": 0.15,
    "valuation": 0.15,
    "risk": 0.15,
    "management": 0.05
}

# ── Financial Health Rules Thresholds ──
MIN_OPERATING_MARGIN_EXCELLENT = 0.20
MIN_OPERATING_MARGIN_STRONG = 0.10
MIN_OPERATING_MARGIN_AVERAGE = 0.05

MIN_ROE_STRONG = 0.15
MIN_ROE_AVERAGE = 0.05

MAX_DEBT_TO_EQUITY_CRITICAL = 2.5
MAX_DEBT_TO_EQUITY_WARNING = 1.5

MIN_CURRENT_RATIO_SAFE = 1.2
MIN_CURRENT_RATIO_WARNING = 0.8

# ── Growth Rules Thresholds ──
MIN_REVENUE_GROWTH_EXCELLENT = 0.15
MIN_REVENUE_GROWTH_STRONG = 0.08
MIN_REVENUE_GROWTH_AVERAGE = 0.02

MIN_NET_INCOME_GROWTH_STRONG = 0.05

# ── Valuation Rules Thresholds ──
MAX_PE_RATIO_BENCHMARK = 35.0
MIN_PE_RATIO_CHEAP = 15.0

# ── Business Quality Rules Thresholds ──
MIN_EMPLOYEES_LARGE_SCALE = 10000
MIN_EMPLOYEES_MID_SCALE = 1000
