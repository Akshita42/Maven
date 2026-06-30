# ─────────────────────────────────────────────────────────────────
# src/report/constants.py
# ─────────────────────────────────────────────────────────────────
#
# Constants for the Investment Report Generator.
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class ReportStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
