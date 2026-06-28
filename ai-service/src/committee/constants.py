# ─────────────────────────────────────────────────────────────────
# src/committee/constants.py
# ─────────────────────────────────────────────────────────────────
#
# Centralized constants and enums for the Investment Committee.
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class ReviewerType(str, Enum):
    BUSINESS = "BUSINESS"
    FINANCIAL = "FINANCIAL"
    VALUATION = "VALUATION"
    RISK = "RISK"
    GOVERNANCE = "GOVERNANCE"

class OpinionRecommendation(str, Enum):
    SUPPORT = "SUPPORT"
    QUESTION = "QUESTION"
    REJECT = "REJECT"

class ReviewStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class ConflictSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
