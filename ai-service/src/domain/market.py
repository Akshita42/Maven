# ─────────────────────────────────────────────────────────────────
# src/domain/market.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain Model representing Market Price metrics.
# Independent of Yahoo Finance or any external vendor.
# ─────────────────────────────────────────────────────────────────

from typing import Optional
from pydantic import BaseModel

class MarketData(BaseModel):
    """Authoritative business model for market pricing and indicator metrics."""
    currentPrice: Optional[float] = None
    previousClose: Optional[float] = None
    fiftyTwoWeekHigh: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    currency: str = "USD"
    
    # Retrieval status metadata
    retrieved_successfully: bool = False
