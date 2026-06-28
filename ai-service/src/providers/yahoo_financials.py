# ─────────────────────────────────────────────────────────────────
# src/providers/yahoo_financials.py
# ─────────────────────────────────────────────────────────────────
#
# Yahoo Fundamentals Timeseries API Provider.
#
# Retrieves quarterly and annual income statements, balance sheets,
# and cash flows crumb-free. Maps keys cleanly to core domain models.
# ─────────────────────────────────────────────────────────────────

import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
from src.utils.logger import logger
from src.core.http_client import HttpClient
from src.providers.base import FinancialsProvider
from src.constants.financial_mapping import FINANCIAL_FIELD_MAP
from src.domain.financials import (
    CompanyFinancials, 
    IncomeStatement, 
    BalanceSheet, 
    CashFlowStatement,
    CompletenessScore,
    ProviderMetadata,
    FinancialField,
    CoverageMetrics,
    ValidationReport,
    ValidationResult
)

TIMESERIES_API_URL = "https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries"

def get_query_types() -> List[str]:
    """Retrieves all query types from the centralized FINANCIAL_FIELD_MAP."""
    types = []
    for canonical_key, freq_map in FINANCIAL_FIELD_MAP.items():
        types.append(freq_map["annual"])
        types.append(freq_map["quarterly"])
    return types

class YahooFinancialsProvider(FinancialsProvider):
    """
    Scrapes Yahoo fundamentals-timeseries API crumb-free.
    Decoupled mapping boundaries ensure no external field names leak to domain layer.
    """
    PARSER_VERSION = "1.2.0"
    PROVIDER_NAME = "Yahoo Finance Timeseries API"

    def __init__(self, http_client: HttpClient = None):
        self.http_client = http_client or HttpClient()

    def fetch_financial_statements(self, ticker: str) -> CompanyFinancials:
        """
        Ingests financial statements from timeseries API.
        Maps raw values, extracts dates/years/quarters, and builds provenance envelopes.
        """
        start_time = time.perf_counter()
        logger.info(f"METRIC: provider_cache_lookup name=financials_provider ticker={ticker} status=miss")
        
        # Build query parameters dynamically from centralized map
        type_labels = get_query_types()
        encoded_ticker = urllib.parse.quote(ticker)
        query_types = ",".join(type_labels)
        
        url = f"{TIMESERIES_API_URL}/{encoded_ticker}?symbol={encoded_ticker}&type={query_types}&period1=0&period2=2000000000"
        
        try:
            payload = self.http_client.execute_json(url)
            results = payload.get("timeseries", {}).get("result", [])
            
            retrieved_at_timestamp = datetime.utcnow().isoformat() + "Z"
            
            if not results:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=financials_provider ticker={ticker} status=empty")
                return self._build_empty_financials(ticker)

            # 1. Group data values by (frequency, date) -> variable_name -> raw_value
            currency = "USD"
            data_map: Dict[str, Dict[str, Dict[str, int]]] = {
                "annual": {},
                "quarterly": {}
            }
            
            for r in results:
                meta = r.get("meta", {})
                type_list = meta.get("type", [])
                if not type_list:
                    continue
                raw_type = type_list[0]
                
                # Check currency
                currency_meta = meta.get("currency")
                if currency_meta:
                    currency = currency_meta
                
                # Determine frequency (annual vs quarterly) and locate canonical field name
                freq = None
                canonical_name = None
                
                for canon_key, freq_map in FINANCIAL_FIELD_MAP.items():
                    if freq_map["annual"] == raw_type:
                        freq = "annual"
                        canonical_name = canon_key
                        break
                    elif freq_map["quarterly"] == raw_type:
                        freq = "quarterly"
                        canonical_name = canon_key
                        break
                
                if not freq or not canonical_name:
                    continue
                
                # Parse data entries
                series_data = r.get(raw_type, [])
                for val in series_data:
                    date_str = val.get("asOfDate")
                    reported = val.get("reportedValue")
                    if not date_str or reported is None:
                        continue
                        
                    raw_val = reported.get("raw")
                    if raw_val is None:
                        continue
                    
                    int_val = int(raw_val)
                    
                    if date_str not in data_map[freq]:
                        data_map[freq][date_str] = {}
                    data_map[freq][date_str][canonical_name] = int_val
            
            # 2. Build Statement lists with provenance envelopes
            annual_is: List[IncomeStatement] = []
            quarterly_is: List[IncomeStatement] = []
            annual_bs: List[BalanceSheet] = []
            quarterly_bs: List[BalanceSheet] = []
            annual_cf: List[CashFlowStatement] = []
            quarterly_cf: List[CashFlowStatement] = []
            
            def create_field(val: Optional[int], freq_str: str) -> Optional[FinancialField]:
                if val is None:
                    return None
                return FinancialField(
                    value=val,
                    source=url,
                    provider=self.PROVIDER_NAME,
                    period=freq_str,
                    retrievedAt=retrieved_at_timestamp,
                    confidence=1.0  # Provider raw extraction is fully certain (1.0)
                )

            for freq in ["annual", "quarterly"]:
                for date_str, metrics in data_map[freq].items():
                    try:
                        date_dt = datetime.strptime(date_str, "%Y-%m-%d")
                        year = date_dt.year
                        quarter = (date_dt.month - 1) // 3 + 1
                    except Exception:
                        year = 0
                        quarter = 1
                        
                    is_quarterly = (freq == "quarterly")
                    q_num = quarter if is_quarterly else None
                    
                    is_keys = ["revenue", "costOfRevenue", "grossProfit", "researchDevelopment", 
                               "sellingGeneralAdministrative", "operatingExpenses", "operatingIncome", "netIncome"]
                    bs_keys = ["totalAssets", "totalLiabilities", "stockholdersEquity", 
                               "cashAndCashEquivalents", "longTermDebt", "retainedEarnings", 
                               "currentAssets", "currentLiabilities"]
                    cf_keys = ["operatingCashFlow", "capitalExpenditures", "freeCashFlow"]
                    
                    has_is = any(k in metrics for k in is_keys)
                    has_bs = any(k in metrics for k in bs_keys)
                    has_cf = any(k in metrics for k in cf_keys)
                    
                    if has_is:
                        stmt = IncomeStatement(
                            fiscalYear=year,
                            fiscalQuarter=q_num,
                            periodEndDate=date_str,
                            currency=currency,
                            revenue=create_field(metrics.get("revenue"), freq),
                            costOfRevenue=create_field(metrics.get("costOfRevenue"), freq),
                            grossProfit=create_field(metrics.get("grossProfit"), freq),
                            researchDevelopment=create_field(metrics.get("researchDevelopment"), freq),
                            sellingGeneralAdministrative=create_field(metrics.get("sellingGeneralAdministrative"), freq),
                            operatingExpenses=create_field(metrics.get("operatingExpenses"), freq),
                            operatingIncome=create_field(metrics.get("operatingIncome"), freq),
                            netIncome=create_field(metrics.get("netIncome"), freq)
                        )
                        if is_quarterly:
                            quarterly_is.append(stmt)
                        else:
                            annual_is.append(stmt)
                            
                    if has_bs:
                        stmt = BalanceSheet(
                            fiscalYear=year,
                            fiscalQuarter=q_num,
                            periodEndDate=date_str,
                            currency=currency,
                            totalAssets=create_field(metrics.get("totalAssets"), freq),
                            totalLiabilities=create_field(metrics.get("totalLiabilities"), freq),
                            stockholdersEquity=create_field(metrics.get("stockholdersEquity"), freq),
                            cashAndCashEquivalents=create_field(metrics.get("cashAndCashEquivalents"), freq),
                            longTermDebt=create_field(metrics.get("longTermDebt"), freq),
                            retainedEarnings=create_field(metrics.get("retainedEarnings"), freq),
                            currentAssets=create_field(metrics.get("currentAssets"), freq),
                            currentLiabilities=create_field(metrics.get("currentLiabilities"), freq)
                        )
                        if is_quarterly:
                            quarterly_bs.append(stmt)
                        else:
                            annual_bs.append(stmt)
                            
                    if has_cf:
                        stmt = CashFlowStatement(
                            fiscalYear=year,
                            fiscalQuarter=q_num,
                            periodEndDate=date_str,
                            currency=currency,
                            operatingCashFlow=create_field(metrics.get("operatingCashFlow"), freq),
                            capitalExpenditures=create_field(metrics.get("capitalExpenditures"), freq),
                            freeCashFlow=create_field(metrics.get("freeCashFlow"), freq),
                            netIncome=create_field(metrics.get("netIncome"), freq)
                        )
                        if is_quarterly:
                            quarterly_cf.append(stmt)
                        else:
                            annual_cf.append(stmt)

            # Sort statement lists by end date descending
            annual_is.sort(key=lambda x: x.periodEndDate, reverse=True)
            quarterly_is.sort(key=lambda x: x.periodEndDate, reverse=True)
            annual_bs.sort(key=lambda x: x.periodEndDate, reverse=True)
            quarterly_bs.sort(key=lambda x: x.periodEndDate, reverse=True)
            annual_cf.sort(key=lambda x: x.periodEndDate, reverse=True)
            quarterly_cf.sort(key=lambda x: x.periodEndDate, reverse=True)
            
            # Track completeness percentage
            retrieved_count = 0
            expected_count = 0
            for freq_iter in ["annual", "quarterly"]:
                for date_str, metrics in data_map[freq_iter].items():
                    retrieved_count += len(metrics)
                    expected_count += len(FINANCIAL_FIELD_MAP)
            
            pct = (retrieved_count / expected_count) if expected_count > 0 else 0.0
            completeness = CompletenessScore(
                fieldsExpected=expected_count,
                fieldsRetrieved=retrieved_count,
                completenessPercentage=round(pct, 4)
            )
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            meta_info = ProviderMetadata(
                providerName=self.PROVIDER_NAME,
                providerVersion=self.PARSER_VERSION,
                retrievedAt=retrieved_at_timestamp,
                retrievalMethod="HTTP API JSON",
                status="success",
                providerHealth=1.0,
                latencyMs=elapsed_ms,
                retryCount=0,
                freshnessStatus="fresh",
                ageHours=0.0,
                sourceUrl=url,
                recordsRetrieved=retrieved_count,
                recordsExpected=expected_count,
                qualityScore=round(pct, 4),
                warnings=[],
                errors=[]
            )
            
            empty_coverage = CoverageMetrics(
                incomeStatementCoverage=0.0,
                balanceSheetCoverage=0.0,
                cashFlowCoverage=0.0,
                overallCoverage=0.0
            )
            
            empty_val_report = ValidationReport(
                overallStatus="PASSED",
                passedRules=[],
                failedRules=[],
                warnings=[],
                issues=[],
                validationScore=1.0
            )
            
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=financials_provider ticker={ticker} status=success")
            
            return CompanyFinancials(
                ticker=ticker,
                annualIncomeStatements=annual_is,
                quarterlyIncomeStatements=quarterly_is,
                annualBalanceSheets=annual_bs,
                quarterlyBalanceSheets=quarterly_bs,
                annualCashFlowStatements=annual_cf,
                quarterlyCashFlowStatements=quarterly_cf,
                completeness=completeness,
                coverage=empty_coverage,
                validationReport=empty_val_report,
                qualityScore=0.0,
                meta=meta_info,
                retrieved_successfully=True
            )
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(f"METRIC: provider_latency_ms={elapsed_ms:.2f} name=financials_provider ticker={ticker} status=failure")
            logger.error(f"YahooFinancialsProvider: Statement retrieval failed for '{ticker}': {str(e)}")
            raise TimeoutError(f"Yahoo Financial Statements lookup failed: {str(e)}")

    def _build_empty_financials(self, ticker: str) -> CompanyFinancials:
        """Returns a default CompanyFinancials with 0 completeness score."""
        return CompanyFinancials(
            ticker=ticker,
            completeness=CompletenessScore(fieldsExpected=0, fieldsRetrieved=0, completenessPercentage=0.0),
            coverage=CoverageMetrics(
                incomeStatementCoverage=0.0, balanceSheetCoverage=0.0, cashFlowCoverage=0.0, overallCoverage=0.0
            ),
            validationReport=ValidationReport(
                overallStatus="FAILED", passedRules=[], failedRules=[], warnings=[], issues=[], validationScore=0.0
            ),
            qualityScore=0.0,
            meta=ProviderMetadata(
                providerName=self.PROVIDER_NAME,
                providerVersion=self.PARSER_VERSION,
                retrievedAt=datetime.utcnow().isoformat() + "Z",
                retrievalMethod="HTTP API JSON",
                status="failed",
                providerHealth=0.0,
                latencyMs=0.0,
                retryCount=0,
                freshnessStatus="unknown",
                ageHours=0.0,
                sourceUrl=f"{TIMESERIES_API_URL}/{ticker}",
                recordsRetrieved=0,
                recordsExpected=0,
                qualityScore=0.0,
                warnings=[],
                errors=[]
            ),
            retrieved_successfully=False
        )
