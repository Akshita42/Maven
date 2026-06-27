# ─────────────────────────────────────────────────────────────────
# src/services/evidence_service.py
# ─────────────────────────────────────────────────────────────────
#
# Coordinating Service for Phase 6 Evidence Collection.
#
# Orchestrates structured evidence retrieval using abstract provider
# interfaces resolved via DI/ProviderRegistry. Derives confidence scores
# dynamically from domain data structure success states.
# ─────────────────────────────────────────────────────────────────

from datetime import datetime
from typing import Any, List
from src.utils.logger import logger

from src.domain.evidence import (
    EvidenceField,
    CompanyProfileEvidence,
    MarketDataEvidence,
    NewsItemEvidence,
    EvidencePackage
)
from src.domain.company import CompanyProfile
from src.domain.market import MarketData
from src.domain.news import NewsItem

from src.providers.base import MarketDataProvider, CompanyProfileProvider, NewsProvider
from src.providers.registry import ProviderRegistry

# ── Helper to build EvidenceFields ──

def make_field(value: Any, source: str, confidence: float) -> EvidenceField:
    """Helper to instantiate a standard EvidenceField with retrieval timestamp."""
    return EvidenceField(
        value=value,
        source=source,
        retrievedAt=datetime.utcnow().isoformat() + "Z",
        confidence=confidence
    )

# ── Evidence Collector Coordinator ──

class EvidenceCollector:
    """
    Orchestrates evidence collection.
    Supports DI (Dependency Injection) via constructor parameters.
    Falls back to ProviderRegistry resolution if no providers are supplied.
    """
    def __init__(
        self,
        market_provider: MarketDataProvider = None,
        profile_provider: CompanyProfileProvider = None,
        news_provider: NewsProvider = None
    ):
        # Resolve via DI arguments, defaulting to central ProviderRegistry resolution
        self.market_provider = market_provider or ProviderRegistry.get_market_provider()
        self.profile_provider = profile_provider or ProviderRegistry.get_profile_provider()
        self.news_provider = news_provider or ProviderRegistry.get_news_provider()

    def collect(self, resolver_result: dict) -> EvidencePackage:
        """
        Coordinates evidence retrieval across abstract providers.
        Derives confidence dynamically based on domain data quality.
        """
        ticker = resolver_result.get("ticker")
        resolver_confidence = resolver_result.get("confidence") or 1.0
        
        if not ticker:
            logger.error("EvidenceCollector: Missing ticker symbol in resolver input.")
            raise ValueError("A resolved company ticker symbol is required to collect evidence.")
            
        logger.info(f"EvidenceCollector: Gathering evidence package for symbol '{ticker}'...")
        
        # 1. Fetch News (returns List[NewsItem] domain list)
        raw_news: List[NewsItem] = []
        try:
            raw_news = self.news_provider.fetch_news(ticker)
        except Exception as e:
            logger.error(f"EvidenceCollector: News provider failed: {str(e)}")
            
        # 2. Fetch Market Data (returns MarketData domain model)
        market_data = MarketData()
        try:
            market_data = self.market_provider.fetch_market_data(ticker)
        except Exception as e:
            logger.error(f"EvidenceCollector: Market provider failed: {str(e)}")
            
        # 3. Fetch Profile (returns CompanyProfile domain model)
        profile_data = CompanyProfile(ticker=ticker)
        try:
            profile_data = self.profile_provider.fetch_profile_data(ticker)
        except Exception as e:
            logger.error(f"EvidenceCollector: Profile provider failed: {str(e)}")

        # ── Confidence Score Derivations ──
        # Calculate based on domain model success markers and parameter completeness:
        
        # A. Profile data confidence
        if not profile_data.retrieved_successfully:
            profile_confidence = 0.0
        else:
            missing_profile_penalty = 0.0
            if profile_data.employees is None:
                missing_profile_penalty += 0.2
            if profile_data.businessSummary is None:
                missing_profile_penalty += 0.3
            profile_confidence = max(0.0, resolver_confidence - missing_profile_penalty)

        # B. Market data confidence
        if not market_data.retrieved_successfully:
            market_confidence = 0.0
        else:
            missing_market_penalty = 0.0
            if market_data.currentPrice is None:
                missing_market_penalty += 0.2
            if profile_data.marketCap is None:
                missing_market_penalty += 0.2
            market_confidence = max(0.0, resolver_confidence - missing_market_penalty)

        # C. News data confidence
        news_confidence = resolver_confidence if raw_news else 0.0

        # ── Build Canonical Schema mappings ──
        
        profile_ev = CompanyProfileEvidence(
            companyName=make_field(
                value=resolver_result.get("companyName") or profile_data.companyName,
                source="Company Resolver",
                confidence=resolver_confidence
            ),
            ticker=make_field(
                value=ticker,
                source="Company Resolver",
                confidence=resolver_confidence
            ),
            exchange=make_field(
                value=resolver_result.get("exchange") or profile_data.exchange,
                source="Company Resolver",
                confidence=resolver_confidence
            ),
            sector=make_field(
                value=resolver_result.get("sector") or profile_data.sector or "Unknown",
                source="Company Resolver / Yahoo Profile",
                confidence=profile_confidence
            ),
            industry=make_field(
                value=resolver_result.get("industry") or profile_data.industry or "Unknown",
                source="Company Resolver / Yahoo Profile",
                confidence=profile_confidence
            ),
            country=make_field(
                value=resolver_result.get("country") or profile_data.country or "Unknown",
                source="Company Resolver / Yahoo Profile",
                confidence=profile_confidence
            ),
            currency=make_field(
                value=market_data.currency,
                source="Yahoo Chart API",
                confidence=market_confidence
            ),
            employees=make_field(
                value=profile_data.employees,
                source="Yahoo Profile Page scraper",
                confidence=profile_confidence
            ),
            businessSummary=make_field(
                value=profile_data.businessSummary,
                source="Yahoo Profile Page scraper",
                confidence=profile_confidence
            )
        )

        market_ev = MarketDataEvidence(
            currentPrice=make_field(
                value=market_data.currentPrice,
                source="Yahoo Chart API",
                confidence=market_confidence
            ),
            previousClose=make_field(
                value=market_data.previousClose,
                source="Yahoo Chart API",
                confidence=market_confidence
            ),
            marketCap=make_field(
                value=profile_data.marketCap,
                source="Yahoo Profile Page scraper",
                confidence=profile_confidence
            ),
            fiftyTwoWeekHigh=make_field(
                value=market_data.fiftyTwoWeekHigh,
                source="Yahoo Chart API",
                confidence=market_confidence
            ),
            fiftyTwoWeekLow=make_field(
                value=market_data.fiftyTwoWeekLow,
                source="Yahoo Chart API",
                confidence=market_confidence
            )
        )

        news_ev = []
        for item in raw_news:
            news_ev.append(
                NewsItemEvidence(
                    headline=make_field(item.headline, "Yahoo Search API", news_confidence),
                    publisher=make_field(item.publisher, "Yahoo Search API", news_confidence),
                    publishedAt=make_field(item.publishedAt, "Yahoo Search API", news_confidence),
                    url=make_field(item.url, "Yahoo Search API", news_confidence)
                )
            )

        logger.info(f"EvidenceCollector: Successfully assembled evidence for symbol '{ticker}'.")
        return EvidencePackage(
            companyProfile=profile_ev,
            marketData=market_ev,
            news=news_ev
        )

# ── Backward-compatible Route Coordinator Function ──

def collect_evidence_package(resolver_result: dict) -> EvidencePackage:
    """Coordinating function used by routes."""
    collector = EvidenceCollector()
    return collector.collect(resolver_result)
