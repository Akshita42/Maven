# ─────────────────────────────────────────────────────────────────
# src/constants/scoring_thresholds.py
# ─────────────────────────────────────────────────────────────────
#
# Scoring, Ingestion Completeness, and Freshness Thresholds.
# ─────────────────────────────────────────────────────────────────

# ── Validation Penalties ──
PENALTY_ERROR = 0.2
PENALTY_WARNING = 0.1
PENALTY_INFO = 0.0

# ── Freshness Limits ──
STALE_THRESHOLD_HOURS = 24.0

# ── Completeness Minimums ──
MIN_COMPLETENESS_PERCENTAGE = 0.5
MIN_VALIDATION_SCORE_FOR_PASS = 0.5
