# ─────────────────────────────────────────────────────────────────
# src/domain/evidence.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain components for the Evidence Layer.
# Enforces strict schemas and provenance trails with frozen models.
# ─────────────────────────────────────────────────────────────────

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict
from src.domain.financials import CompanyFinancials

class EvidenceField(BaseModel):
    """Envelope wrapping a resolved data value with its provenance trail."""
    model_config = ConfigDict(frozen=True)
    
    value: Any = None
    source: str
    retrievedAt: str
    confidence: float

class CompanyProfileEvidence(BaseModel):
    """Compiled provenance values for company profiles."""
    model_config = ConfigDict(frozen=True)
    
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
    model_config = ConfigDict(frozen=True)
    
    currentPrice: EvidenceField
    previousClose: EvidenceField
    marketCap: EvidenceField
    fiftyTwoWeekHigh: EvidenceField
    fiftyTwoWeekLow: EvidenceField

class NewsItemEvidence(BaseModel):
    """Compiled provenance values for a news article."""
    model_config = ConfigDict(frozen=True)
    
    headline: EvidenceField
    publisher: EvidenceField
    publishedAt: EvidenceField
    url: EvidenceField

class FinancialsEvidence(BaseModel):
    """Envelope wrapping the compiled historical financial statements package."""
    model_config = ConfigDict(frozen=True)
    
    value: Optional[CompanyFinancials] = None
    source: str
    retrievedAt: str
    confidence: float
