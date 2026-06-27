# ─────────────────────────────────────────────────────────────────
# src/providers/yahoo_chart.py
# ─────────────────────────────────────────────────────────────────
#
# Yahoo Chart API Provider.
#
# Retrieves market price indicators using chart API.
# Inherits from MarketDataProvider base interface. Maps directly to domain.
# ─────────────────────────────────────────────────────────────────

import time
import urllib.parse
from src.utils.logger import logger
from src.core.http_client import HttpClient
from src.providers.base import MarketDataProvider
from src.domain.market import MarketData

CHART_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

class YahooChartProvider(MarketDataProvider):
    """
    Implements MarketDataProvider interface querying Yahoo chart API.
    """
    def __init__(self, http_client: HttpClient = None):
        self.http_client = http_client or HttpClient()

    def fetch_market_data(self, ticker: str) -> MarketData:
        """
        Queries Yahoo v8 chart API and parses raw nodes into a MarketData domain model.
        """
        encoded_ticker = urllib.parse.quote(ticker)
        url = f"{CHART_API_URL}/{encoded_ticker}?range=1d&interval=1d"
        
        start_time = time.perf_counter()
        logger.info(f"METRIC: provider_cache_lookup name=market_provider ticker={ticker} status=miss")
        
        try:
            payload = self.http_client.execute_json(url)
            result = payload.get("chart", {}).get("result", [])
            if not result:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=market_provider ticker={ticker} status=empty")
                return MarketData()
                
            meta = result[0].get("meta", {})
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=market_provider ticker={ticker} status=success")
            
            return MarketData(
                currentPrice=meta.get("regularMarketPrice"),
                previousClose=meta.get("chartPreviousClose"),
                fiftyTwoWeekHigh=meta.get("fiftyTwoWeekHigh"),
                fiftyTwoWeekLow=meta.get("fiftyTwoWeekLow"),
                currency=meta.get("currency", "USD"),
                retrieved_successfully=True
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=market_provider ticker={ticker} status=failure")
            logger.error(f"YahooChartProvider: Price fetch failed for '{ticker}': {str(e)}")
            raise TimeoutError(f"Yahoo Chart lookup failed: {str(e)}")
