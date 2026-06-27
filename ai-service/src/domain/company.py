# ─────────────────────────────────────────────────────────────────
# src/domain/company.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain Model representing a Company entity.
# Independent of Yahoo Finance or any external vendor.
# ─────────────────────────────────────────────────────────────────

from typing import Optional
from pydantic import BaseModel

class CompanyProfile(BaseModel):
    """Authoritative business model for a company's profile description and metadata."""
    companyName: Optional[str] = None
    ticker: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employees: Optional[int] = None
    businessSummary: Optional[str] = None
    marketCap: Optional[int] = None
    
    # Retrieval status metadata
    retrieved_successfully: bool = False
