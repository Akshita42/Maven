# ─────────────────────────────────────────────────────────────────
# src/providers/yahoo_search.py
# ─────────────────────────────────────────────────────────────────
#
# Yahoo Search API Provider.
#
# Retrieves recent news stories using autocomplete search endpoint.
# Inherits from NewsProvider base interface. Maps directly to domain.
# ─────────────────────────────────────────────────────────────────

import time
import urllib.parse
from datetime import datetime
from typing import List
from src.utils.logger import logger
from src.constants.api import YAHOO_SEARCH_URL
from src.core.http_client import HttpClient
from src.providers.base import NewsProvider
from src.domain.news import NewsItem

class YahooSearchProvider(NewsProvider):
    """
    Implements NewsProvider interface querying Yahoo autocomplete search API.
    """
    def __init__(self, http_client: HttpClient = None):
        self.http_client = http_client or HttpClient()

    def fetch_news(self, ticker: str) -> List[NewsItem]:
        """
        Queries Yahoo search autocomplete API and maps results to List[NewsItem] domain models.
        """
        encoded_ticker = urllib.parse.quote(ticker)
        url = f"{YAHOO_SEARCH_URL}?q={encoded_ticker}&newsCount=5"
        
        start_time = time.perf_counter()
        
        # Cache hit rate placeholder hook
        logger.info(f"METRIC: provider_cache_lookup name=news_provider ticker={ticker} status=miss")
        
        try:
            payload = self.http_client.execute_json(url)
            news_quotes = payload.get("news", [])
            
            parsed_items = []
            for item in news_quotes:
                headline = item.get("title", "")
                publisher = item.get("publisher", "Unknown")
                published_unix = item.get("providerPublishTime")
                url_link = item.get("link", "")
                
                # Convert unix epoch to ISO timestamp
                published_iso = ""
                if published_unix:
                    try:
                        published_iso = datetime.utcfromtimestamp(published_unix).isoformat() + "Z"
                    except Exception:
                        pass
                
                parsed_items.append(
                    NewsItem(
                        headline=headline,
                        publisher=publisher,
                        publishedAt=published_iso,
                        url=url_link
                    )
                )
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Latency metric hook
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=news_provider ticker={ticker} status=success")
            
            return parsed_items
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Failure count & Latency metrics hook
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=news_provider ticker={ticker} status=failure")
            logger.error(f"YahooSearchProvider: News lookup failed for '{ticker}': {str(e)}")
            
            raise TimeoutError(f"Yahoo News lookup failed: {str(e)}")
