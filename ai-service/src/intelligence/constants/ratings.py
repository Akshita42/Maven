# ─────────────────────────────────────────────────────────────────
# src/intelligence/constants/ratings.py
# ─────────────────────────────────────────────────────────────────
#
# Deterministic score-to-rating threshold mapping.
# ─────────────────────────────────────────────────────────────────

from src.intelligence.constants.enums import Rating

def get_rating_for_score(score: float) -> Rating:
    """Returns the strongly typed Rating enum for a given score (0.0 - 10.0)."""
    if score >= 8.5:
        return Rating.EXCELLENT
    elif score >= 7.0:
        return Rating.STRONG
    elif score >= 5.0:
        return Rating.AVERAGE
    elif score >= 3.0:
        return Rating.WEAK
    else:
        return Rating.CRITICAL
