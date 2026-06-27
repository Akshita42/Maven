# ─────────────────────────────────────────────────────────────────
# src/domain/evidence.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain Model representing the compiled Evidence Package.
# Enforces strict schemas and provenance trails.
# ─────────────────────────────────────────────────────────────────

from typing import Any, List
from pydantic import BaseModel

class EvidenceField(BaseModel):
    """Envelope wrapping a resolved data value with its provenance trail."""
    value: Any = None
    source: str
    retrievedAt: str
    confidence: float

class CompanyProfileEvidence(BaseModel):
    """Compiled provenance values for company profiles."""
    companyName: EvidenceField
    ticker: EvidenceField
    exchange: EvidenceField
    sector: EvidenceField
    industry: EvidenceField
    country: EvidenceField
    currency: EvidenceField
    employees: EvidenceField
    businessSummary: EvidenceField

class MarketDataEvidence(BaseModel):
    """Compiled provenance values for market indicators."""
    currentPrice: EvidenceField
    previousClose: EvidenceField
    marketCap: EvidenceField
    fiftyTwoWeekHigh: EvidenceField
    fiftyTwoWeekLow: EvidenceField

class NewsItemEvidence(BaseModel):
    """Compiled provenance values for a news article."""
    headline: EvidenceField
    publisher: EvidenceField
    publishedAt: EvidenceField
    url: EvidenceField

class EvidencePackage(BaseModel):
    """The complete canonical evidence package model."""
    companyProfile: CompanyProfileEvidence
    marketData: MarketDataEvidence
    news: List[NewsItemEvidence]
