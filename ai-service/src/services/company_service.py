# ─────────────────────────────────────────────────────────────────
# src/services/company_service.py
# ─────────────────────────────────────────────────────────────────
#
# Typed Company Resolution Pipeline Service.
#
# Implements a pure scoring function, a typed candidate model,
# a typed output model, query pre-normalization, candidate count capping,
# and structured ambiguity explanations.
# ─────────────────────────────────────────────────────────────────

import json
import time
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.utils.logger import logger
from src.constants.api import YAHOO_SEARCH_URL

# ── Named Scoring Constants ──
SCORE_BASE_EQUITY = 50.0
SCORE_ETF_PENALTY = -30.0
SCORE_EXACT_TICKER = 100.0
SCORE_EXACT_NAME = 45.0
SCORE_ACRONYM_MATCH = 40.0
SCORE_PARTIAL_NAME = 15.0
SCORE_YAHOO_TOP_RESULT = 30.0
SCORE_US_PRIMARY_EXCHANGE = 35.0
SCORE_MAJOR_EXCHANGE = 10.0

# ── Threshold Constants ──
MIN_RESOLUTION_SCORE = 40.0
AMBIGUITY_GAP_THRESHOLD = 35.0
MAX_EXPECTED_SCORE = 220.0
YAHOO_REQUEST_TIMEOUT = 8.0
MAX_CANDIDATES_TO_EVALUATE = 20

# Set of major U.S. and international exchanges mapped to countries
EXCHANGE_COUNTRY_MAP = {
    "NASDAQ": "United States",
    "NYSE": "United States",
    "NMS": "United States",
    "NYQ": "United States",
    "NYS": "United States",
    "ASE": "United States",
    "TORONTO": "Canada",
    "TSX": "Canada",
    "SWISS": "Switzerland",
    "EBS": "Switzerland",
    "TOKYO": "Japan",
    "BOMBAY": "India",
    "NSE": "India",
    "LONDON": "United Kingdom",
    "LSE": "United Kingdom",
    "FRANKFURT": "Germany",
    "XETRA": "Germany",
}

# Standard corporate suffixes to strip for clean name matching
CORP_SUFFIXES = [
    "INC.", "INC", "CORPORATION", "CORP.", "CORP", "COMPANY", "CO.", "CO",
    "LIMITED", "LTD.", "LTD", "PLC.", "PLC", "SA", "AG", "SE"
]

class Candidate(BaseModel):
    """
    Immutable representation of a company candidate during evaluation.
    Stores raw Yahoo Finance data and accumulated score results.
    """
    symbol: str
    shortname: Optional[str] = None
    longname: Optional[str] = None
    quoteType: str
    exchange: str
    exchDisp: str
    score: float = 0.0
    reasons: List[str] = Field(default_factory=list)
    raw_quote: Dict[str, Any]

class ResolverResult(BaseModel):
    """
    Canonical output schema for the Company Resolver intelligence module.
    Exposes only the stable contract properties.
    """
    resolved: bool
    ticker: Optional[str] = None
    companyName: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    aliases: Optional[List[str]] = None
    confidence: Optional[float] = None
    confidenceLevel: Optional[str] = None
    resolutionReason: Optional[List[str]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    ambiguityReason: Optional[str] = None
    resolutionStrategy: str = "Deterministic Ranking"
    processingTimeMs: Optional[float] = None

def clean_corporate_name(name: str) -> str:
    """Strips common corporate suffixes to allow clean text comparison."""
    parts = name.upper().split()
    cleaned = [p for p in parts if p not in CORP_SUFFIXES]
    return " ".join(cleaned) if cleaned else name.upper()

# ── Pipeline Functions ──

def fetch_candidates(normalized_query: str, timeout_seconds: float = YAHOO_REQUEST_TIMEOUT) -> List[Dict[str, Any]]:
    """
    Step 1: Fetch candidate list from Yahoo Finance Search API.
    Enforces a strict network timeout to avoid blocking downstream services.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    encoded_query = urllib.parse.quote(normalized_query)
    url = f"{YAHOO_SEARCH_URL}?q={encoded_query}&newsCount=0"
    
    logger.info(f"Issuing HTTP request to Yahoo Finance API: {url}")
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            if response.status != 200:
                logger.error(f"Yahoo Search failed with HTTP status: {response.status}")
                return []
            
            payload = json.loads(response.read().decode('utf-8'))
            quotes = payload.get("quotes", [])
            logger.info(f"Retrieved {len(quotes)} candidates from Yahoo Finance.")
            return quotes
    except Exception as e:
        logger.error(f"Network exception or timeout during Yahoo lookup: {str(e)}")
        # Raise controlled error to be caught at route handler
        raise TimeoutError("External financial data lookup timed out or failed.")

def filter_candidates(quotes: List[Dict[str, Any]]) -> List[Candidate]:
    """
    Step 2: Filter and map raw quotes to Candidate models.
    Keeps only EQUITY and ETF security types.
    """
    filtered = []
    for quote in quotes:
        quote_type = quote.get("quoteType", "").upper()
        if quote_type in ["EQUITY", "ETF"]:
            # Parse properties safely
            symbol = quote.get("symbol", "").upper()
            shortname = quote.get("shortname")
            longname = quote.get("longname")
            exchange = quote.get("exchange", "")
            exch_disp = quote.get("exchDisp", "")
            
            filtered.append(
                Candidate(
                    symbol=symbol,
                    shortname=shortname,
                    longname=longname,
                    quoteType=quote_type,
                    exchange=exchange,
                    exchDisp=exch_disp,
                    raw_quote=quote
                )
            )
    return filtered

def score_candidate(candidate: Candidate, normalized_query: str, max_yahoo_score: float, rank_index: int) -> Candidate:
    """
    Step 3 (Pure helper): Scores a single candidate deterministically.
    Does not mutate the input; returns a new Candidate instance.
    """
    score = 0.0
    reasons = []

    # A. Security Type check
    if candidate.quoteType == "EQUITY":
        score += SCORE_BASE_EQUITY
        reasons.append("Equity security identified")
    else:
        score += SCORE_ETF_PENALTY # Negative weighting

    # B. Ticker symbol matching
    if normalized_query == candidate.symbol:
        score += SCORE_EXACT_TICKER
        reasons.append("Exact ticker matched")

    # C. Name comparison
    clean_query = clean_corporate_name(normalized_query)
    
    if candidate.shortname:
        clean_short = clean_corporate_name(candidate.shortname)
        if clean_query == clean_short:
            score += SCORE_EXACT_NAME
            reasons.append("Exact company name matched")
        elif clean_query in clean_short or clean_short in clean_query:
            score += SCORE_PARTIAL_NAME
            reasons.append("Search name match")

    if candidate.longname:
        clean_long = clean_corporate_name(candidate.longname)
        
        # Check acronym
        words = clean_long.split()
        acronym = "".join([w[0] for w in words if len(w) > 0])
        
        if clean_query == clean_long:
            score += SCORE_EXACT_NAME
            if "Exact company name matched" not in reasons:
                reasons.append("Exact company name matched")
        elif clean_query == acronym:
            score += SCORE_ACRONYM_MATCH
            reasons.append("Company acronym matched")
        elif clean_query in clean_long or clean_long in clean_query:
            score += SCORE_PARTIAL_NAME
            if "Search name match" not in reasons:
                reasons.append("Search name match")

    # D. Exchange checking
    is_us_primary = False
    is_major_exchange = False
    
    exchange_upper = candidate.exchange.upper()
    exch_disp_upper = candidate.exchDisp.upper()
    
    if exchange_upper in ["NMS", "NYQ", "NYS", "ASE", "NGM"] or exch_disp_upper in ["NASDAQ", "NYSE", "NYSE MKT", "AMEX"]:
        is_us_primary = True
        is_major_exchange = True
    else:
        for exch_key in EXCHANGE_COUNTRY_MAP:
            if exch_key in exchange_upper or exch_key in exch_disp_upper:
                is_major_exchange = True
                break
    
    if is_us_primary:
        score += SCORE_US_PRIMARY_EXCHANGE
        reasons.append("Primary U.S. listing selected")
    elif is_major_exchange:
        score += SCORE_MAJOR_EXCHANGE
        reasons.append("Major exchange listing identified")

    # E. Yahoo Score Weighting
    yahoo_score = candidate.raw_quote.get("score", 0)
    if max_yahoo_score > 0:
        score += (yahoo_score / max_yahoo_score) * 50.0
        
    if rank_index == 0:
        score += SCORE_YAHOO_TOP_RESULT
        reasons.append("Yahoo Search #1 Ranking")

    # Add general fallback selection reason
    reasons.append("Highest ranking candidate")

    # Return a new Candidate instance (immutable design)
    return Candidate(
        symbol=candidate.symbol,
        shortname=candidate.shortname,
        longname=candidate.longname,
        quoteType=candidate.quoteType,
        exchange=candidate.exchange,
        exchDisp=candidate.exchDisp,
        score=score,
        reasons=reasons,
        raw_quote=candidate.raw_quote
    )

def score_candidates(filtered_quotes: List[Candidate], normalized_query: str) -> List[Candidate]:
    """
    Step 3 (Orchestration): Iterates through filtered candidates and calls the pure scoring function.
    """
    scored = []
    max_yahoo_score = max([c.raw_quote.get("score", 0) for c in filtered_quotes]) if filtered_quotes else 0
    
    for i, candidate in enumerate(filtered_quotes):
        scored.append(score_candidate(candidate, normalized_query, max_yahoo_score, i))
        
    # Sort scored candidates in descending order
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored

def choose_best_candidate(scored_candidates: List[Candidate], normalized_query: str) -> ResolverResult:
    """
    Step 4: Resolve candidate or handle ambiguity.
    Exposes only the canonical ResolverResult Pydantic contract.
    """
    if not scored_candidates:
        return ResolverResult(
            resolved=False,
            ambiguityReason=f"No publicly traded equities found matching search '{normalized_query}'."
        )

    # Ambiguity gap checking
    if len(scored_candidates) > 1:
        top_cand = scored_candidates[0]
        second_cand = scored_candidates[1]
        
        if (top_cand.score - second_cand.score) < AMBIGUITY_GAP_THRESHOLD:
            candidates_list = []
            for item in scored_candidates[:5]:
                q = item.raw_quote
                candidates_list.append({
                    "companyName": q.get("longname") or q.get("shortname") or q.get("symbol"),
                    "ticker": q.get("symbol"),
                    "exchange": q.get("exchDisp") or q.get("exchange")
                })
            
            return ResolverResult(
                resolved=False,
                ambiguityReason="ambiguous_candidates_found",
                candidates=candidates_list
            )

    winner = scored_candidates[0]
    win_quote = winner.raw_quote
    win_score = winner.score
    
    if win_score < MIN_RESOLUTION_SCORE:
        return ResolverResult(
            resolved=False,
            ambiguityReason=f"No high-confidence match found for query '{normalized_query}'."
        )

    # Generate aliases dynamically
    aliases = []
    symbol = winner.symbol
    shortname = winner.shortname
    longname = winner.longname
    
    if symbol:
        aliases.append(symbol)
    if shortname and shortname not in aliases:
        aliases.append(shortname)
    if longname and longname not in aliases:
        aliases.append(longname)

    # Resolve Country
    resolved_country = "Unknown"
    win_exchange = winner.exchange.upper()
    win_exch_disp = winner.exchDisp.upper()
    
    for exch_key, country in EXCHANGE_COUNTRY_MAP.items():
        if exch_key in win_exchange or exch_key in win_exch_disp:
            resolved_country = country
            break

    # Calculate confidence & derive level
    confidence = min(round(win_score / MAX_EXPECTED_SCORE, 2), 1.0)
    
    if confidence >= 0.85:
        confidence_level = "Very High"
    elif confidence >= 0.70:
        confidence_level = "High"
    elif confidence >= 0.50:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    # Filter out duplicate reasons
    clean_reasons = []
    for r in winner.reasons:
        if r not in clean_reasons:
            clean_reasons.append(r)

    # Return the typed Pydantic result model matching the canonical contract
    return ResolverResult(
        resolved=True,
        companyName=win_quote.get("longname") or win_quote.get("shortname") or winner.symbol,
        ticker=winner.symbol,
        exchange=win_quote.get("exchDisp") or winner.exchange,
        sector=win_quote.get("sector", "Unknown"),
        industry=win_quote.get("industry", "Unknown"),
        country=resolved_country,
        aliases=aliases,
        confidence=confidence,
        confidenceLevel=confidence_level,
        resolutionReason=clean_reasons
    )

# ── Main Coordinator Function ──

from functools import lru_cache

@lru_cache(maxsize=128)
def resolve_company_metadata(query: str) -> ResolverResult:
    """
    Coordinating function for the Company Resolver pipeline.
    
    TODO: Implement company resolution caching to prevent high-frequency API hits
    and improve latency.
    """
    # Normalize query once at the top of the pipeline
    normalized_query = query.strip().upper()
    
    # Strip common intent prefixes for cleaner resolution
    import re
    # Remove common words at the beginning
    normalized_query = re.sub(r'^(ANALYZE|RESEARCH|EVALUATE|REVIEW|LOOK\s*UP)\s+', '', normalized_query).strip()
    
    logger.info(f"Starting company entity resolution query: '{normalized_query}'")
    start_time = time.time()
    
    # 1. Fetch Candidates
    candidates = fetch_candidates(normalized_query, timeout_seconds=YAHOO_REQUEST_TIMEOUT)
    
    # 2. Filter Candidates
    filtered = filter_candidates(candidates)
    
    # 3. Limit candidates evaluated to 20 maximum
    limited = filtered[:MAX_CANDIDATES_TO_EVALUATE]
    
    # 4. Score Candidates (Pure iteration)
    scored = score_candidates(limited, normalized_query)
    
    # 5. Choose Best Candidate
    resolution = choose_best_candidate(scored, normalized_query)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    resolution.processingTimeMs = duration_ms
    
    if resolution.resolved:
        logger.info(
            f"Successfully resolved query '{normalized_query}' to '{resolution.ticker}' "
            f"in {duration_ms}ms with {resolution.confidenceLevel} confidence ({resolution.confidence})."
        )
    else:
        logger.warn(
            f"Failed to resolve query '{normalized_query}' in {duration_ms}ms. "
            f"Reason: {resolution.ambiguityReason or 'No matches'}"
        )
        
    return resolution
