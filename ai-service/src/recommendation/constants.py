# ─────────────────────────────────────────────────────────────────
# src/recommendation/constants.py
# ─────────────────────────────────────────────────────────────────
#
# Enums and constants for the Investment Recommendation Layer.
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class InvestmentStance(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class TimeHorizon(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    MEDIUM_TERM = "MEDIUM_TERM"
    LONG_TERM = "LONG_TERM"

class ConvictionLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RecommendationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
