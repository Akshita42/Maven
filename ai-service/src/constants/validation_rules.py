# ─────────────────────────────────────────────────────────────────
# src/constants/validation_rules.py
# ─────────────────────────────────────────────────────────────────
#
# Centrally Defined Validation Rules.
# ─────────────────────────────────────────────────────────────────

VALIDATION_RULES = {
    "FIN-001": {
        "ruleName": "RevenueRange",
        "severity": "WARNING",
        "message": "Negative revenue detected. Please verify company is non-pre-revenue."
    },
    "FIN-002": {
        "ruleName": "TotalAssetsRange",
        "severity": "ERROR",
        "message": "Total assets must be positive. Zero/negative total assets violates accounting logic."
    },
    "FIN-003": {
        "ruleName": "CashConsistency",
        "severity": "ERROR",
        "message": "Cash and Cash Equivalents cannot exceed Total Assets."
    },
    "FIN-004": {
        "ruleName": "DateChronology",
        "severity": "ERROR",
        "message": "Financial statements are not sorted in strict descending chronological order."
    },
    "FIN-005": {
        "ruleName": "DuplicateYears",
        "severity": "ERROR",
        "message": "Duplicate fiscal years detected in the annual statements list."
    },
    "FIN-006": {
        "ruleName": "QuarterlyYearMatch",
        "severity": "WARNING",
        "message": "Quarterly reporting date year deviates significantly from fiscal year designation."
    }
}
