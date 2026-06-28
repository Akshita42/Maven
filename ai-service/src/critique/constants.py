# ─────────────────────────────────────────────────────────────────
# src/critique/constants.py
# ─────────────────────────────────────────────────────────────────
#
# Centralized constants and enums for the Self-Critique Layer.
# ─────────────────────────────────────────────────────────────────

from enum import Enum

class BiasCategory(str, Enum):
    CONFIRMATION = "CONFIRMATION"
    ANCHORING = "ANCHORING"
    AVAILABILITY = "AVAILABILITY"
    RECENCY = "RECENCY"
    SELECTION = "SELECTION"

class CritiquePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKING = "BLOCKING"

class CritiqueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class CritiqueStatus(str, Enum):
    SUCCESS = "SUCCESS"
    DEGRADED = "DEGRADED"  # Set if AI engine fails but deterministic calculations succeed
