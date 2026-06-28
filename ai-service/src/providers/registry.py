# ─────────────────────────────────────────────────────────────────
# src/providers/registry.py
# ─────────────────────────────────────────────────────────────────
#
# Provider Registry.
#
# Central registry for resolving provider implementations.
# Supports swap-outs and config-driven registrations without modifying
# consumer service implementations.
# ─────────────────────────────────────────────────────────────────

from src.providers.base import (
    MarketDataProvider, 
    CompanyProfileProvider, 
    NewsProvider,
    FinancialsProvider
)
from src.providers.yahoo_chart import YahooChartProvider
from src.providers.yahoo_profile import YahooProfileProvider
from src.providers.yahoo_search import YahooSearchProvider
from src.providers.yahoo_financials import YahooFinancialsProvider

class ProviderRegistry:
    """
    Central repository registry managing provider instances.
    Provides a base decoupling layer for future Dependency Injection hook-ins.
    """
    _market_provider: MarketDataProvider = None
    _profile_provider: CompanyProfileProvider = None
    _news_provider: NewsProvider = None
    _financials_provider: FinancialsProvider = None

    @classmethod
    def register_market_provider(cls, provider: MarketDataProvider):
        cls._market_provider = provider

    @classmethod
    def register_profile_provider(cls, provider: CompanyProfileProvider):
        cls._profile_provider = provider

    @classmethod
    def register_news_provider(cls, provider: NewsProvider):
        cls._news_provider = provider

    @classmethod
    def register_financials_provider(cls, provider: FinancialsProvider):
        cls._financials_provider = provider

    @classmethod
    def get_market_provider(cls) -> MarketDataProvider:
        if cls._market_provider is None:
            # Default fallback registry
            cls._market_provider = YahooChartProvider()
        return cls._market_provider

    @classmethod
    def get_profile_provider(cls) -> CompanyProfileProvider:
        if cls._profile_provider is None:
            cls._profile_provider = YahooProfileProvider()
        return cls._profile_provider

    @classmethod
    def get_news_provider(cls) -> NewsProvider:
        if cls._news_provider is None:
            cls._news_provider = YahooSearchProvider()
        return cls._news_provider

    @classmethod
    def get_financials_provider(cls) -> FinancialsProvider:
        if cls._financials_provider is None:
            cls._financials_provider = YahooFinancialsProvider()
        return cls._financials_provider
