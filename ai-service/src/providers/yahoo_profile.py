# ─────────────────────────────────────────────────────────────────
# src/providers/yahoo_profile.py
# ─────────────────────────────────────────────────────────────────
#
# Yahoo Profile HTML Scraper Provider.
#
# Scrapes profile metadata using HTML scraping and deserialization.
# Inherits from CompanyProfileProvider interface. Maps directly to domain.
# ─────────────────────────────────────────────────────────────────

import time
import json
import re
import urllib.parse
from typing import Optional
from src.utils.logger import logger
from src.core.http_client import HttpClient
from src.providers.base import CompanyProfileProvider
from src.domain.company import CompanyProfile

QUOTE_PAGE_URL = "https://finance.yahoo.com/quote"

class YahooProfileProvider(CompanyProfileProvider):
    """
    Implements CompanyProfileProvider scraping corporate profile data from Yahoo HTML.
    """
    def __init__(self, http_client: HttpClient = None):
        self.http_client = http_client or HttpClient()

    def fetch_profile_data(self, ticker: str) -> CompanyProfile:
        """
        Orchestration pipeline. Returns clean domain model.
        """
        start_time = time.perf_counter()
        logger.info(f"METRIC: provider_cache_lookup name=profile_provider ticker={ticker} status=miss")
        
        try:
            html = self._download_html(ticker)
            if not html:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=profile_provider ticker={ticker} status=empty")
                return CompanyProfile(ticker=ticker)

            script_content = self._extract_json_block(html, ticker)
            if not script_content:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=profile_provider ticker={ticker} status=empty")
                return CompanyProfile(ticker=ticker)

            deserialized_data = self._deserialize_json_block(script_content)
            if not deserialized_data:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=profile_provider ticker={ticker} status=empty")
                return CompanyProfile(ticker=ticker)

            profile = self._map_to_profile(deserialized_data, ticker)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=profile_provider ticker={ticker} status=success")
            return profile
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=profile_provider ticker={ticker} status=failure")
            logger.error(f"YahooProfileProvider: Profile collection failed for '{ticker}': {str(e)}")
            raise TimeoutError(f"Yahoo Profile lookup failed: {str(e)}")

    # ── Pipeline Helper Functions ──

    def _download_html(self, ticker: str) -> Optional[str]:
        """Step 1: Download raw quote HTML from Yahoo Finance."""
        encoded_ticker = urllib.parse.quote(ticker)
        url = f"{QUOTE_PAGE_URL}/{encoded_ticker}/"
        logger.info(f"YahooProfileProvider: Downloading HTML quote page: {url}")
        
        # Shared HttpClient manages compression, retries, and headers
        raw_bytes = self.http_client.execute(url)
        return raw_bytes.decode('utf-8')

    def _extract_json_block(self, html: str, ticker: str) -> Optional[str]:
        """Step 2: Locate and extract the preloaded JSON state script block."""
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for s in scripts:
            s_strip = s.strip()
            # Check for signature preloaded state keys
            if 'fulltimeemployees' in s_strip.lower() and 'quotesummary' in s_strip.lower():
                logger.info(f"YahooProfileProvider: Found preloaded state script (len={len(s_strip)}) for '{ticker}'.")
                return s_strip
                
        logger.warn(f"YahooProfileProvider: Preloaded state script block missing in HTML for '{ticker}'.")
        return None

    def _deserialize_json_block(self, script_content: str) -> Optional[dict]:
        """Step 3: Parse the outer JSON and nested body JSON strings."""
        try:
            parsed_json = json.loads(script_content)
            if 'body' not in parsed_json:
                logger.error("YahooProfileProvider: 'body' key missing in parsed script tag.")
                return None
                
            body_json = json.loads(parsed_json['body'])
            return body_json
        except json.JSONDecodeError as je:
            logger.error(f"YahooProfileProvider: JSON state deserialization failed: {str(je)}")
            return None

    def _map_to_profile(self, body_json: dict, ticker: str) -> CompanyProfile:
        """Step 4: Map raw JSON nodes into CompanyProfile domain model."""
        qs = body_json.get("quoteSummary", {}).get("result", [])
        if not qs:
            logger.warn(f"YahooProfileProvider: quoteSummary result empty for '{ticker}'.")
            return CompanyProfile(ticker=ticker)

        result_block = qs[0]
        profile = result_block.get("summaryProfile", {})
        price = result_block.get("price", {})

        # Extract values safely
        employees = profile.get("fullTimeEmployees")
        summary = profile.get("longBusinessSummary")
        market_cap = price.get("marketCap", {}).get("raw")
        sector = profile.get("sector")
        industry = profile.get("industry")
        country = profile.get("country")
        
        long_name = price.get("longName") or price.get("longname")
        short_name = price.get("shortName") or price.get("shortname")
        display_name = price.get("displayName")
        symbol = price.get("symbol")
        
        company_name = long_name or short_name or display_name or symbol or ticker

        logger.info(f"YahooProfileProvider: Mapped profile result model for '{ticker}' successfully.")
        return CompanyProfile(
            companyName=company_name,
            ticker=ticker,
            employees=employees,
            businessSummary=summary,
            marketCap=market_cap,
            sector=sector,
            industry=industry,
            country=country,
            retrieved_successfully=True
        )
