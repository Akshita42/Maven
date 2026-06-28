# ─────────────────────────────────────────────────────────────────
# src/providers/base.py
# ─────────────────────────────────────────────────────────────────
#
# Base Provider Interfaces.
#
# Connects abstract provider methods with core Domain models.
# ─────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
from typing import List
from src.domain.company import CompanyProfile
from src.domain.market import MarketData
from src.domain.news import NewsItem
from src.domain.financials import CompanyFinancials

# ── Provider Interfaces (Abstract Classes) ──

class MarketDataProvider(ABC):
    """Abstract interface for retrieving market pricing models."""
    @abstractmethod
    def fetch_market_data(self, ticker: str) -> MarketData:
        pass

class CompanyProfileProvider(ABC):
    """Abstract interface for retrieving company profile models."""
    @abstractmethod
    def fetch_profile_data(self, ticker: str) -> CompanyProfile:
        pass

class NewsProvider(ABC):
    """Abstract interface for retrieving corporate news listings."""
    @abstractmethod
    def fetch_news(self, ticker: str) -> List[NewsItem]:
        pass

class FinancialsProvider(ABC):
    """Abstract interface for retrieving audited historical statements."""
    @abstractmethod
    def fetch_financial_statements(self, ticker: str) -> CompanyFinancials:
        pass
