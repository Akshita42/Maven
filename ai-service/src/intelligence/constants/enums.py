# ─────────────────────────────────────────────────────────────────
# src/intelligence/constants/enums.py
# ─────────────────────────────────────────────────────────────────
#
# Strongly-typed string enums for the Investment Intelligence Layer.
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class AnalyzerStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class Rating(str, Enum):
    EXCELLENT = "EXCELLENT"
    STRONG = "STRONG"
    AVERAGE = "AVERAGE"
    WEAK = "WEAK"
    CRITICAL = "CRITICAL"

class RuleSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"

class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"
