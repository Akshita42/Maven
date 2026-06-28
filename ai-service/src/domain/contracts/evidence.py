# ─────────────────────────────────────────────────────────────────
# src/domain/contracts/evidence.py
# ─────────────────────────────────────────────────────────────────
#
# Stable API contract for the ValidatedEvidencePackage.
# Exposes only externally stable properties across boundaries.
# ─────────────────────────────────────────────────────────────────

from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict
from src.domain.evidence import (
    CompanyProfileEvidence,
    MarketDataEvidence,
    NewsItemEvidence,
    FinancialsEvidence
)
from src.domain.financials import ProviderMetadata, ValidationReport

class EvidencePackage(BaseModel):
    """
    The stable externally exposed API contract for ValidatedEvidencePackage.
    Immutable, versioned, and complete package representing consolidated evidence.
    """
    model_config = ConfigDict(frozen=True)
    
    schemaVersion: str = "1.0.0"
    evidenceId: str
    retrievedAt: str
    validatedAt: str
    
    # Root level independent diagnostics scores
    resolutionConfidence: float
    qualityScore: float
    validationScore: float
    validationReport: ValidationReport
    
    # Nested provenance segments
    companyProfile: CompanyProfileEvidence
    marketData: MarketDataEvidence
    news: List[NewsItemEvidence]
    financials: FinancialsEvidence
    
    # Provider result metadata map (e.g. financials, profile, market, news)
    providers: Dict[str, ProviderMetadata]

# Alias for contract renaming alignment
ValidatedEvidencePackage = EvidencePackage
