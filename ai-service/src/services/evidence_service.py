# ─────────────────────────────────────────────────────────────────
# src/services/evidence_service.py
# ─────────────────────────────────────────────────────────────────
#
# Coordinating Service for Phase 6 & 7 Evidence Collection.
#
# Orchestrates structured evidence retrieval using abstract provider
# interfaces. Computes statement coverage, derived metrics + data lineage,
# ValidationReport with centrally managed validation rules, trend
# analysis with confidence, and data quality scores. All models are frozen.
# ─────────────────────────────────────────────────────────────────

import time
import uuid
import urllib.parse
from datetime import datetime
from typing import Any, List, Optional, Dict
from src.utils.logger import logger

from src.constants.api import YAHOO_SEARCH_URL
from src.constants.scoring_thresholds import (
    PENALTY_ERROR,
    PENALTY_WARNING,
    PENALTY_INFO,
    STALE_THRESHOLD_HOURS
)
from src.constants.validation_rules import VALIDATION_RULES

from src.domain.evidence import (
    EvidenceField,
    CompanyProfileEvidence,
    MarketDataEvidence,
    NewsItemEvidence,
    FinancialsEvidence
)
from src.domain.contracts.evidence import EvidencePackage
from src.domain.company import CompanyProfile
from src.domain.market import MarketData
from src.domain.news import NewsItem
from src.domain.financials import (
    CompanyFinancials,
    FinancialField,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    ValidationResult,
    ValidationReport,
    CoverageMetrics,
    DerivedFinancialMetrics,
    FinancialMetricsPeriod,
    TrendMetric,
    FinancialTrends,
    CompletenessScore,
    ProviderMetadata
)

from src.providers.base import (
    MarketDataProvider, 
    CompanyProfileProvider, 
    NewsProvider,
    FinancialsProvider
)
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

# ── Freshness calculation helper ──

def get_freshness(retrieved_at_str: str) -> tuple:
    """Calculates age in hours and freshness status from retrieved ISO timestamp."""
    try:
        retrieved_dt = datetime.strptime(retrieved_at_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
    except Exception:
        try:
            retrieved_dt = datetime.strptime(retrieved_at_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return "unknown", 0.0
            
    age = (datetime.utcnow() - retrieved_dt).total_seconds() / 3600.0
    status = "fresh" if age < STALE_THRESHOLD_HOURS else "stale"
    return status, round(age, 4)

# ── Financial Ingestion Analytics & Validation Functions ──

def calculate_coverage(financials: CompanyFinancials) -> CoverageMetrics:
    """Calculates coverage scores per statement type and overall."""
    # 1. Income Statement
    is_expected = (len(financials.annualIncomeStatements) + len(financials.quarterlyIncomeStatements)) * 8
    is_retrieved = 0
    for stmt in financials.annualIncomeStatements + financials.quarterlyIncomeStatements:
        for f in [stmt.revenue, stmt.costOfRevenue, stmt.grossProfit, stmt.researchDevelopment,
                  stmt.sellingGeneralAdministrative, stmt.operatingExpenses, stmt.operatingIncome, stmt.netIncome]:
            if f is not None and f.value is not None:
                is_retrieved += 1
                
    # 2. Balance Sheet
    bs_expected = (len(financials.annualBalanceSheets) + len(financials.quarterlyBalanceSheets)) * 8
    bs_retrieved = 0
    for stmt in financials.annualBalanceSheets + financials.quarterlyBalanceSheets:
        for f in [stmt.totalAssets, stmt.totalLiabilities, stmt.stockholdersEquity, stmt.cashAndCashEquivalents,
                  stmt.longTermDebt, stmt.retainedEarnings, stmt.currentAssets, stmt.currentLiabilities]:
            if f is not None and f.value is not None:
                bs_retrieved += 1
                
    # 3. Cash Flow Statement
    cf_expected = (len(financials.annualCashFlowStatements) + len(financials.quarterlyCashFlowStatements)) * 4
    cf_retrieved = 0
    for stmt in financials.annualCashFlowStatements + financials.quarterlyCashFlowStatements:
        for f in [stmt.operatingCashFlow, stmt.capitalExpenditures, stmt.freeCashFlow, stmt.netIncome]:
            if f is not None and f.value is not None:
                cf_retrieved += 1
                
    total_expected = is_expected + bs_expected + cf_expected
    total_retrieved = is_retrieved + bs_retrieved + cf_retrieved
    
    return CoverageMetrics(
        incomeStatementCoverage=round(is_retrieved / is_expected, 4) if is_expected > 0 else 0.0,
        balanceSheetCoverage=round(bs_retrieved / bs_expected, 4) if bs_expected > 0 else 0.0,
        cashFlowCoverage=round(cf_retrieved / cf_expected, 4) if cf_expected > 0 else 0.0,
        overallCoverage=round(total_retrieved / total_expected, 4) if total_expected > 0 else 0.0
    )

def validate_financial_statements(ticker: str, financials: CompanyFinancials) -> ValidationReport:
    """Performs range, range consistency, chronology, and duplicate mappings checks."""
    passed = []
    failed = []
    warnings = []
    issues = []
    penalty_accum = 0.0
    
    def evaluate_rule(rule_id: str, assertion_passed: bool, dynamic_msg_suffix: str = ""):
        rule = VALIDATION_RULES[rule_id]
        if assertion_passed:
            passed.append(rule["ruleName"])
        else:
            issue = ValidationResult(
                severity=rule["severity"],
                ruleId=rule_id,
                message=rule["message"] + dynamic_msg_suffix
            )
            issues.append(issue)
            
            # Map severity to warning vs failed list and accumulate penalty
            if rule["severity"] == "ERROR":
                failed.append(issue)
                nonlocal penalty_accum
                penalty_accum += PENALTY_ERROR
            elif rule["severity"] == "WARNING":
                warnings.append(issue)
                penalty_accum += PENALTY_WARNING
            else:
                penalty_accum += PENALTY_INFO

    # 1. Check Revenue non-negativity (FIN-001)
    rev_neg_count = sum(1 for stmt in financials.annualIncomeStatements + financials.quarterlyIncomeStatements
                        if stmt.revenue and stmt.revenue.value is not None and stmt.revenue.value < 0)
    evaluate_rule("FIN-001", rev_neg_count == 0, f" (Found {rev_neg_count} violations)")

    # 2. Check Total Assets positivity (FIN-002)
    assets_err_count = sum(1 for stmt in financials.annualBalanceSheets + financials.quarterlyBalanceSheets
                          if stmt.totalAssets and stmt.totalAssets.value is not None and stmt.totalAssets.value <= 0)
    evaluate_rule("FIN-002", assets_err_count == 0, f" (Found {assets_err_count} violations)")

    # 3. Check Cash <= Assets (FIN-003)
    cash_exceed_count = sum(1 for stmt in financials.annualBalanceSheets + financials.quarterlyBalanceSheets
                            if (stmt.cashAndCashEquivalents and stmt.totalAssets and
                                stmt.cashAndCashEquivalents.value is not None and stmt.totalAssets.value is not None and
                                stmt.cashAndCashEquivalents.value > stmt.totalAssets.value))
    evaluate_rule("FIN-003", cash_exceed_count == 0, f" (Found {cash_exceed_count} violations)")

    # 4. Check Date Chronology (FIN-004)
    date_err = False
    for stmt_list in [financials.annualIncomeStatements, financials.annualBalanceSheets, financials.annualCashFlowStatements]:
        for idx in range(len(stmt_list) - 1):
            if stmt_list[idx].periodEndDate <= stmt_list[idx + 1].periodEndDate:
                date_err = True
                break
    evaluate_rule("FIN-004", not date_err)

    # 5. Check Duplicate Fiscal Years (FIN-005)
    dup_year = False
    for stmt_list in [financials.annualIncomeStatements, financials.annualBalanceSheets, financials.annualCashFlowStatements]:
        years = [stmt.fiscalYear for stmt in stmt_list if stmt.fiscalYear > 0]
        if len(years) != len(set(years)):
            dup_year = True
            break
    evaluate_rule("FIN-005", not dup_year)

    # 6. Check Quarterly date year matches fiscal year +/- 1 (FIN-006)
    quarter_year_err = 0
    for stmt in financials.quarterlyIncomeStatements + financials.quarterlyBalanceSheets + financials.quarterlyCashFlowStatements:
        try:
            date_dt = datetime.strptime(stmt.periodEndDate, "%Y-%m-%d")
            if abs(date_dt.year - stmt.fiscalYear) > 1:
                quarter_year_err += 1
        except Exception:
            pass
    evaluate_rule("FIN-006", quarter_year_err == 0, f" (Found {quarter_year_err} violations)")

    # Derive overall status
    val_score = max(0.0, 1.0 - penalty_accum)
    if val_score < 0.5:
        overall_status = "FAILED"
    elif val_score < 1.0:
        overall_status = "WARNING"
    else:
        overall_status = "PASSED"

    return ValidationReport(
        overallStatus=overall_status,
        validationScore=round(val_score, 4),
        passedRules=passed,
        failedRules=failed,
        warnings=warnings,
        issues=issues
    )

def compute_derived_metrics(financials: CompanyFinancials) -> None:
    """Computes annual and quarterly derived metrics and preserves full data lineage."""
    # Data lineages definitions mapping calculated metrics to raw required properties
    LINEAGE_MAP = {
        "grossMargin": ["grossProfit", "revenue"],
        "operatingMargin": ["operatingIncome", "revenue"],
        "netMargin": ["netIncome", "revenue"],
        "freeCashFlowMargin": ["freeCashFlow", "revenue"],
        "returnOnEquity": ["netIncome", "stockholdersEquity"],
        "returnOnAssets": ["netIncome", "totalAssets"],
        "debtToEquity": ["longTermDebt", "stockholdersEquity"],
        "currentRatio": ["currentAssets", "currentLiabilities"],
        "cashRatio": ["cashAndCashEquivalents", "currentLiabilities"],
        "revenueGrowthYoY": ["revenue"],
        "netIncomeGrowthYoY": ["netIncome"],
        "freeCashFlowGrowthYoY": ["freeCashFlow"]
    }

    for freq in ["annual", "quarterly"]:
        is_map: Dict[str, IncomeStatement] = {}
        bs_map: Dict[str, BalanceSheet] = {}
        cf_map: Dict[str, CashFlowStatement] = {}
        
        is_list = financials.quarterlyIncomeStatements if freq == "quarterly" else financials.annualIncomeStatements
        bs_list = financials.quarterlyBalanceSheets if freq == "quarterly" else financials.annualBalanceSheets
        cf_list = financials.quarterlyCashFlowStatements if freq == "quarterly" else financials.annualCashFlowStatements
        
        for stmt in is_list:
            is_map[stmt.periodEndDate] = stmt
        for stmt in bs_list:
            bs_map[stmt.periodEndDate] = stmt
        for stmt in cf_list:
            cf_map[stmt.periodEndDate] = stmt
            
        all_dates = sorted(list(set(list(is_map.keys()) + list(bs_map.keys()) + list(cf_map.keys()))))
        
        # 1. First pass: compute all non-growth ratios into intermediate dictionary
        raw_ratios: Dict[str, dict] = {}
        
        for date_str in all_dates:
            stmt_is = is_map.get(date_str)
            stmt_bs = bs_map.get(date_str)
            stmt_cf = cf_map.get(date_str)
            
            f_year = 0
            f_quarter = None
            if stmt_is:
                f_year = stmt_is.fiscalYear
                f_quarter = stmt_is.fiscalQuarter
            elif stmt_bs:
                f_year = stmt_bs.fiscalYear
                f_quarter = stmt_bs.fiscalQuarter
            elif stmt_cf:
                f_year = stmt_cf.fiscalYear
                f_quarter = stmt_cf.fiscalQuarter
                
            def val(f: Optional[FinancialField]) -> Optional[int]:
                return f.value if (f is not None) else None
                
            rev = val(stmt_is.revenue) if stmt_is else None
            gp = val(stmt_is.grossProfit) if stmt_is else None
            op_inc = val(stmt_is.operatingIncome) if stmt_is else None
            ni = val(stmt_is.netIncome) if stmt_is else None
            
            assets = val(stmt_bs.totalAssets) if stmt_bs else None
            equity = val(stmt_bs.stockholdersEquity) if stmt_bs else None
            lt_debt = val(stmt_bs.longTermDebt) if stmt_bs else None
            cash = val(stmt_bs.cashAndCashEquivalents) if stmt_bs else None
            curr_assets = val(stmt_bs.currentAssets) if stmt_bs else None
            curr_liabs = val(stmt_bs.currentLiabilities) if stmt_bs else None
            
            fcf = val(stmt_cf.freeCashFlow) if stmt_cf else None
            
            gross_margin = (gp / rev) if (gp is not None and rev and rev != 0) else None
            op_margin = (op_inc / rev) if (op_inc is not None and rev and rev != 0) else None
            net_margin = (ni / rev) if (ni is not None and rev and rev != 0) else None
            fcf_margin = (fcf / rev) if (fcf is not None and rev and rev != 0) else None
            
            roe = (ni / equity) if (ni is not None and equity and equity != 0) else None
            roa = (ni / assets) if (ni is not None and assets and assets != 0) else None
            
            debt_equity = (lt_debt / equity) if (lt_debt is not None and equity and equity != 0) else None
            curr_ratio = (curr_assets / curr_liabs) if (curr_assets is not None and curr_liabs and curr_liabs != 0) else None
            cash_ratio = (cash / curr_liabs) if (cash is not None and curr_liabs and curr_liabs != 0) else None
            
            raw_ratios[date_str] = {
                "fiscalYear": f_year,
                "fiscalQuarter": f_quarter,
                "grossMargin": round(gross_margin, 4) if gross_margin is not None else None,
                "operatingMargin": round(op_margin, 4) if op_margin is not None else None,
                "netMargin": round(net_margin, 4) if net_margin is not None else None,
                "freeCashFlowMargin": round(fcf_margin, 4) if fcf_margin is not None else None,
                "returnOnEquity": round(roe, 4) if roe is not None else None,
                "returnOnAssets": round(roa, 4) if roa is not None else None,
                "debtToEquity": round(debt_equity, 4) if debt_equity is not None else None,
                "currentRatio": round(curr_ratio, 4) if curr_ratio is not None else None,
                "cashRatio": round(cash_ratio, 4) if cash_ratio is not None else None,
                "revenueGrowthYoY": None,
                "netIncomeGrowthYoY": None,
                "freeCashFlowGrowthYoY": None
            }
            
        # 2. Second pass: compute YoY Growth using chronological comparison
        sorted_dates = sorted(all_dates)
        for idx in range(len(sorted_dates)):
            curr_date = sorted_dates[idx]
            curr_r = raw_ratios[curr_date]
            
            prev_date = None
            if freq == "annual":
                if idx > 0:
                    prev_date = sorted_dates[idx - 1]
            else:
                # Find same quarter of the previous fiscal year
                for p_idx in range(idx - 1, -1, -1):
                    p_date = sorted_dates[p_idx]
                    p_r = raw_ratios[p_date]
                    if p_r["fiscalQuarter"] == curr_r["fiscalQuarter"] and p_r["fiscalYear"] == curr_r["fiscalYear"] - 1:
                        prev_date = p_date
                        break
            
            if prev_date:
                curr_is = is_map.get(curr_date)
                prev_is = is_map.get(prev_date)
                curr_cf = cf_map.get(curr_date)
                prev_cf = cf_map.get(prev_date)
                
                curr_rev = val(curr_is.revenue) if curr_is else None
                prev_rev = val(prev_is.revenue) if prev_is else None
                curr_ni = val(curr_is.netIncome) if curr_is else None
                prev_ni = val(prev_is.netIncome) if prev_is else None
                curr_fcf = val(curr_cf.freeCashFlow) if curr_cf else None
                prev_fcf = val(prev_cf.freeCashFlow) if prev_cf else None
                
                if curr_rev is not None and prev_rev:
                    curr_r["revenueGrowthYoY"] = round((curr_rev - prev_rev) / prev_rev, 4)
                if curr_ni is not None and prev_ni:
                    curr_r["netIncomeGrowthYoY"] = round((curr_ni - prev_ni) / prev_ni, 4)
                if curr_fcf is not None and prev_fcf:
                    curr_r["freeCashFlowGrowthYoY"] = round((curr_fcf - prev_fcf) / prev_fcf, 4)

        # 3. Third pass: instantiate frozen Pydantic metrics models
        metrics_list: List[FinancialMetricsPeriod] = []
        for date_str in all_dates:
            r = raw_ratios[date_str]
            computed = DerivedFinancialMetrics(
                grossMargin=r["grossMargin"],
                operatingMargin=r["operatingMargin"],
                netMargin=r["netMargin"],
                freeCashFlowMargin=r["freeCashFlowMargin"],
                returnOnEquity=r["returnOnEquity"],
                returnOnAssets=r["returnOnAssets"],
                debtToEquity=r["debtToEquity"],
                currentRatio=r["currentRatio"],
                cashRatio=r["cashRatio"],
                revenueGrowthYoY=r["revenueGrowthYoY"],
                netIncomeGrowthYoY=r["netIncomeGrowthYoY"],
                freeCashFlowGrowthYoY=r["freeCashFlowGrowthYoY"]
            )
            
            metrics_list.append(
                FinancialMetricsPeriod(
                    fiscalYear=r["fiscalYear"],
                    fiscalQuarter=r["fiscalQuarter"],
                    periodEndDate=date_str,
                    metrics=computed,
                    lineage=LINEAGE_MAP
                )
            )

        metrics_list.sort(key=lambda x: x.periodEndDate, reverse=True)
        if freq == "quarterly":
            quarterly_derived = metrics_list
        else:
            annual_derived = metrics_list
            
    return annual_derived, quarterly_derived

def compute_financial_trends(financials: CompanyFinancials) -> FinancialTrends:
    """Computes historical trend vectors and maps direction confidence."""
    ann_is = sorted(financials.annualIncomeStatements, key=lambda x: x.periodEndDate)
    ann_cf = sorted(financials.annualCashFlowStatements, key=lambda x: x.periodEndDate)
    
    def val(f: Optional[FinancialField]) -> Optional[int]:
        return f.value if (f is not None) else None

    # 1. Revenue Trend
    revs = [val(stmt.revenue) for stmt in ann_is if stmt.revenue and val(stmt.revenue) is not None]
    if len(revs) < 2:
        rev_trend = TrendMetric(direction="Insufficient Data", confidence=0.0, supportingPeriods=0)
    else:
        growths = [(revs[i] - revs[i - 1]) / revs[i - 1] for i in range(1, len(revs)) if revs[i - 1] != 0]
        avg_g = sum(growths) / len(growths) if growths else 0.0
        
        if avg_g > 0.02:
            dir_str = "Growing"
            matching = sum(1 for g in growths if g > 0)
        elif avg_g < -0.02:
            dir_str = "Declining"
            matching = sum(1 for g in growths if g < 0)
        else:
            dir_str = "Flat"
            matching = sum(1 for g in growths if abs(g) <= 0.05)
            
        conf = round(matching / len(growths), 4) if growths else 0.5
        rev_trend = TrendMetric(direction=dir_str, confidence=conf, supportingPeriods=matching)

    # 2. Net Income Trend
    nis = [val(stmt.netIncome) for stmt in ann_is if stmt.netIncome and val(stmt.netIncome) is not None]
    if len(nis) < 2:
        ni_trend = TrendMetric(direction="Insufficient Data", confidence=0.0, supportingPeriods=0)
    else:
        changes = [nis[i] - nis[i - 1] for i in range(1, len(nis))]
        improving_count = sum(1 for c in changes if c > 0)
        deteriorating_count = sum(1 for c in changes if c < 0)
        
        signs = [1 if c >= 0 else -1 for c in changes]
        sign_swings = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])
        
        if sign_swings >= 2 or (improving_count > 0 and deteriorating_count > 0 and abs(improving_count - deteriorating_count) <= 1):
            dir_str = "Volatile"
            conf = round(sign_swings / len(changes), 4)
            supporting = sign_swings
        elif sum(changes) > 0:
            dir_str = "Improving"
            conf = round(improving_count / len(changes), 4)
            supporting = improving_count
        else:
            dir_str = "Deteriorating"
            conf = round(deteriorating_count / len(changes), 4)
            supporting = deteriorating_count
            
        ni_trend = TrendMetric(direction=dir_str, confidence=conf, supportingPeriods=supporting)

    # 3. Cash Flow Trend
    ocfs = [val(stmt.operatingCashFlow) for stmt in ann_cf if stmt.operatingCashFlow and val(stmt.operatingCashFlow) is not None]
    if len(ocfs) < 2:
        cf_trend = TrendMetric(direction="Insufficient Data", confidence=0.0, supportingPeriods=0)
    else:
        positive_count = sum(1 for o in ocfs if o > 0)
        negative_count = sum(1 for o in ocfs if o < 0)
        
        if positive_count == len(ocfs):
            dir_str = "Positive"
            conf = 1.0
            supporting = positive_count
        elif negative_count == len(ocfs):
            dir_str = "Negative"
            conf = 1.0
            supporting = negative_count
        else:
            dir_str = "Highly Variable"
            conf = round(abs(positive_count - negative_count) / len(ocfs), 4)
            supporting = max(positive_count, negative_count)
            
        cf_trend = TrendMetric(direction=dir_str, confidence=conf, supportingPeriods=supporting)

    return FinancialTrends(
        revenueTrend=rev_trend,
        netIncomeTrend=ni_trend,
        cashFlowTrend=cf_trend
    )

# ── Evidence Collector Coordinator ──

class EvidenceCollector:
    """
    Orchestrates evidence collection including profile, market, news, and financials.
    Supports DI (Dependency Injection) via constructor parameters.
    Falls back to ProviderRegistry resolution if no providers are supplied.
    """
    def __init__(
        self,
        market_provider: MarketDataProvider = None,
        profile_provider: CompanyProfileProvider = None,
        news_provider: NewsProvider = None,
        financials_provider: FinancialsProvider = None
    ):
        self.market_provider = market_provider or ProviderRegistry.get_market_provider()
        self.profile_provider = profile_provider or ProviderRegistry.get_profile_provider()
        self.news_provider = news_provider or ProviderRegistry.get_news_provider()
        self.financials_provider = financials_provider or ProviderRegistry.get_financials_provider()

    def collect(self, resolver_result: dict) -> EvidencePackage:
        """
        Coordinates evidence retrieval across abstract providers.
        Calculates and maps provider results, diagnostic details, validation rules,
        and returns the frozen external EvidencePackage.
        """
        start_time = time.perf_counter()
        retrieved_at_timestamp = datetime.utcnow().isoformat() + "Z"
        
        ticker = resolver_result.get("ticker")
        resolver_confidence = resolver_result.get("confidence") or 1.0
        
        if not ticker:
            logger.error("EvidenceCollector: Missing ticker symbol in resolver input.")
            raise ValueError("A resolved company ticker symbol is required to collect evidence.")
            
        logger.info(f"EvidenceCollector: Gathering evidence package for symbol '{ticker}'...")
        
        provider_results: Dict[str, ProviderMetadata] = {}
        
        # Helper to construct individual provider diagnostic entries
        def build_provider_meta(
            name: str, version: str, method: str, status: str,
            health: float, latency: float, url: str, retrieved_at: str,
            retrieved: int, expected: int, quality: float,
            warnings_list: List[str] = None, errors_list: List[str] = None
        ) -> ProviderMetadata:
            freshness_status, age_hours = get_freshness(retrieved_at)
            return ProviderMetadata(
                providerName=name,
                providerVersion=version,
                retrievalMethod=method,
                status=status,
                providerHealth=health,
                latencyMs=round(latency, 2),
                retryCount=0,
                retrievedAt=retrieved_at,
                freshnessStatus=freshness_status,
                ageHours=age_hours,
                sourceUrl=url,
                recordsRetrieved=retrieved,
                recordsExpected=expected,
                qualityScore=quality,
                warnings=warnings_list or [],
                errors=errors_list or []
            )

        # ── 1. Fetch Profile ──
        profile_start = time.perf_counter()
        profile_url = f"https://finance.yahoo.com/quote/{urllib.parse.quote(ticker)}/"
        profile_data = CompanyProfile(ticker=ticker)
        profile_status = "failed"
        profile_health = 0.0
        profile_errors = []
        
        try:
            profile_data = self.profile_provider.fetch_profile_data(ticker)
            if profile_data.retrieved_successfully:
                profile_status = "success"
                profile_health = 1.0
            else:
                profile_status = "empty"
                profile_health = 0.8
        except Exception as e:
            profile_errors.append(str(e))
            logger.error(f"EvidenceCollector: Profile provider failed: {str(e)}")
            
        profile_latency = (time.perf_counter() - profile_start) * 1000.0
        
        # Profile records mapping diagnostic counts
        profile_fields = [profile_data.employees, profile_data.businessSummary, profile_data.marketCap,
                          profile_data.sector, profile_data.industry, profile_data.country]
        profile_retrieved_count = sum(1 for f in profile_fields if f is not None)
        profile_expected_count = len(profile_fields)
        profile_quality = round(profile_retrieved_count / profile_expected_count, 4) if profile_expected_count > 0 else 0.0
        
        provider_results["profile"] = build_provider_meta(
            name="Yahoo Profile Scraper",
            version="1.0.0",
            method="HTTP HTML Scraping",
            status=profile_status,
            health=profile_health,
            latency=profile_latency,
            url=profile_url,
            retrieved_at=retrieved_at_timestamp,
            retrieved=profile_retrieved_count,
            expected=profile_expected_count,
            quality=profile_quality,
            errors_list=profile_errors
        )

        # ── 2. Fetch Market Data ──
        market_start = time.perf_counter()
        market_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?range=1d&interval=1d"
        market_data = MarketData()
        market_status = "failed"
        market_health = 0.0
        market_errors = []
        
        try:
            market_data = self.market_provider.fetch_market_data(ticker)
            if market_data.retrieved_successfully:
                market_status = "success"
                market_health = 1.0
            else:
                market_status = "empty"
                market_health = 0.8
        except Exception as e:
            market_errors.append(str(e))
            logger.error(f"EvidenceCollector: Market provider failed: {str(e)}")
            
        market_latency = (time.perf_counter() - market_start) * 1000.0
        
        # Market records mapping diagnostic counts
        market_fields = [market_data.currentPrice, market_data.previousClose, market_data.fiftyTwoWeekHigh, market_data.fiftyTwoWeekLow]
        market_retrieved_count = sum(1 for f in market_fields if f is not None)
        market_expected_count = len(market_fields)
        market_quality = round(market_retrieved_count / market_expected_count, 4) if market_expected_count > 0 else 0.0
        
        provider_results["market"] = build_provider_meta(
            name="Yahoo Chart API",
            version="1.0.0",
            method="HTTP API JSON",
            status=market_status,
            health=market_health,
            latency=market_latency,
            url=market_url,
            retrieved_at=retrieved_at_timestamp,
            retrieved=market_retrieved_count,
            expected=market_expected_count,
            quality=market_quality,
            errors_list=market_errors
        )

        # ── 3. Fetch News ──
        news_start = time.perf_counter()
        news_url = f"{YAHOO_SEARCH_URL}?q={urllib.parse.quote(ticker)}&newsCount=5"
        raw_news: List[NewsItem] = []
        news_status = "failed"
        news_health = 0.0
        news_errors = []
        
        try:
            raw_news = self.news_provider.fetch_news(ticker)
            if raw_news:
                news_status = "success"
                news_health = 1.0
            else:
                news_status = "empty"
                news_health = 0.8
        except Exception as e:
            news_errors.append(str(e))
            logger.error(f"EvidenceCollector: News provider failed: {str(e)}")
            
        news_latency = (time.perf_counter() - news_start) * 1000.0
        news_retrieved_count = len(raw_news)
        news_expected_count = 5
        news_quality = round(news_retrieved_count / news_expected_count, 4) if news_expected_count > 0 else 0.0
        
        provider_results["news"] = build_provider_meta(
            name="Yahoo Search Autocomplete",
            version="1.0.0",
            method="HTTP API JSON",
            status=news_status,
            health=news_health,
            latency=news_latency,
            url=news_url,
            retrieved_at=retrieved_at_timestamp,
            retrieved=news_retrieved_count,
            expected=news_expected_count,
            quality=news_quality,
            errors_list=news_errors
        )

        # ── 4. Fetch Financial Statements ──
        financials_start = time.perf_counter()
        financial_statements = None
        financials_error_reason = ""
        financials_status = "failed"
        financials_health = 0.0
        financials_errors = []
        financials_url = f"https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{urllib.parse.quote(ticker)}"
        
        try:
            financial_statements = self.financials_provider.fetch_financial_statements(ticker)
            if financial_statements.retrieved_successfully:
                financials_status = "success"
                financials_health = 1.0
            else:
                financials_status = "empty"
                financials_health = 0.8
        except Exception as e:
            financials_error_reason = str(e)
            financials_errors.append(financials_error_reason)
            logger.error(f"EvidenceCollector: Financials provider failed for '{ticker}': {financials_error_reason}")

        financials_latency = (time.perf_counter() - financials_start) * 1000.0

        # Compile and calculate metrics if financials succeeded
        if financial_statements and financial_statements.retrieved_successfully:
            cov_metrics = calculate_coverage(financial_statements)
            financials_dict = financial_statements.model_dump()
            
            # A. Set coverage metrics
            financials_dict["coverage"] = cov_metrics.model_dump()
            
            # B. Validation check
            val_report = validate_financial_statements(ticker, financial_statements)
            financials_dict["validationReport"] = val_report.model_dump()
            
            # C. Derived metrics & trend calculations
            annual_derived, quarterly_derived = compute_derived_metrics(financial_statements)
            financials_dict["annualDerivedMetrics"] = [m.model_dump() for m in annual_derived]
            financials_dict["quarterlyDerivedMetrics"] = [m.model_dump() for m in quarterly_derived]
            
            # Instantiate temp statements for trend calculation
            temp_statements = CompanyFinancials(**financials_dict)
            trends_calc = compute_financial_trends(temp_statements)
            financials_dict["trends"] = trends_calc.model_dump()
            
            # D. Compute Quality Score
            quality = round(cov_metrics.overallCoverage * val_report.validationScore * financials_health, 4)
            financials_dict["qualityScore"] = quality
            
            # Package financials mapping
            financial_statements_model = CompanyFinancials(**financials_dict)
            
            # Complete financials provider metadata mapping
            provider_results["financials"] = build_provider_meta(
                name=financial_statements_model.meta.providerName,
                version=financial_statements_model.meta.providerVersion,
                method="HTTP API JSON",
                status=financials_status,
                health=financials_health,
                latency=financials_latency,
                url=financials_url,
                retrieved_at=retrieved_at_timestamp,
                retrieved=financial_statements_model.completeness.fieldsRetrieved,
                expected=financial_statements_model.completeness.fieldsExpected,
                quality=financial_statements_model.completeness.completenessPercentage,
                errors_list=financials_errors
            )
        else:
            val_report = ValidationReport(
                overallStatus="FAILED",
                validationScore=0.0,
                passedRules=[],
                failedRules=[],
                warnings=[],
                issues=[]
            )
            quality = 0.0
            financial_statements_model = None
            
            provider_results["financials"] = build_provider_meta(
                name="Yahoo Finance Timeseries API",
                version="1.2.0",
                method="HTTP API JSON",
                status=financials_status,
                health=financials_health,
                latency=financials_latency,
                url=financials_url,
                retrieved_at=retrieved_at_timestamp,
                retrieved=0,
                expected=0,
                quality=0.0,
                errors_list=financials_errors
            )

        # ── Confidence Score Derivations ──
        # confidence score represents only the confidence that the resolver correctly identified the company.
        resolution_confidence = resolver_confidence

        # ── Quality Score Derivation ──
        # represents overall package data quality (coverage + provider status + presence factors)
        news_presence = 1.0 if raw_news else 0.8
        profile_presence = 1.0 if profile_data.retrieved_successfully else 0.5
        overall_quality_score = round(quality * news_presence * profile_presence, 4)

        # ── Validation Score Derivation ──
        # represents validation reports health
        overall_validation_score = val_report.validationScore

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
                confidence=resolver_confidence
            ),
            industry=make_field(
                value=resolver_result.get("industry") or profile_data.industry or "Unknown",
                source="Company Resolver / Yahoo Profile",
                confidence=resolver_confidence
            ),
            country=make_field(
                value=resolver_result.get("country") or profile_data.country or "Unknown",
                source="Company Resolver / Yahoo Profile",
                confidence=resolver_confidence
            ),
            currency=make_field(
                value=market_data.currency or "USD",
                source="Yahoo Chart API",
                confidence=resolver_confidence
            ),
            employees=make_field(
                value=profile_data.employees,
                source="Yahoo Profile Page scraper",
                confidence=resolver_confidence
            ),
            businessSummary=make_field(
                value=profile_data.businessSummary,
                source="Yahoo Profile Page scraper",
                confidence=resolver_confidence
            )
        )

        market_ev = MarketDataEvidence(
            currentPrice=make_field(
                value=market_data.currentPrice,
                source="Yahoo Chart API",
                confidence=resolver_confidence
            ),
            previousClose=make_field(
                value=market_data.previousClose,
                source="Yahoo Chart API",
                confidence=resolver_confidence
            ),
            marketCap=make_field(
                value=profile_data.marketCap,
                source="Yahoo Profile Page scraper",
                confidence=resolver_confidence
            ),
            fiftyTwoWeekHigh=make_field(
                value=market_data.fiftyTwoWeekHigh,
                source="Yahoo Chart API",
                confidence=resolver_confidence
            ),
            fiftyTwoWeekLow=make_field(
                value=market_data.fiftyTwoWeekLow,
                source="Yahoo Chart API",
                confidence=resolver_confidence
            )
        )

        news_ev = []
        for item in raw_news:
            news_ev.append(
                NewsItemEvidence(
                    headline=make_field(item.headline, "Yahoo Search API", resolver_confidence),
                    publisher=make_field(item.publisher, "Yahoo Search API", resolver_confidence),
                    publishedAt=make_field(item.publishedAt, "Yahoo Search API", resolver_confidence),
                    url=make_field(item.url, "Yahoo Search API", resolver_confidence)
                )
            )

        financials_ev = FinancialsEvidence(
            value=financial_statements_model,
            source=financials_url,
            retrievedAt=retrieved_at_timestamp,
            confidence=resolver_confidence
        )

        # Generate unique Evidence Ingest GUID and validation timestamps
        evidence_guid = str(uuid.uuid4())
        validated_at_timestamp = datetime.utcnow().isoformat() + "Z"

        # Emit Observability Metric logging
        logger.info(
            f"PROVIDER_METRIC ticker={ticker} evidenceId={evidence_guid} "
            f"resolutionConfidence={resolution_confidence} qualityScore={overall_quality_score} "
            f"validationScore={overall_validation_score} validationStatus={val_report.overallStatus}"
        )

        # Returns the frozen external API contract
        return EvidencePackage(
            schemaVersion="1.0.0",
            evidenceId=evidence_guid,
            retrievedAt=retrieved_at_timestamp,
            validatedAt=validated_at_timestamp,
            resolutionConfidence=resolution_confidence,
            qualityScore=overall_quality_score,
            validationScore=overall_validation_score,
            validationReport=val_report,
            companyProfile=profile_ev,
            marketData=market_ev,
            news=news_ev,
            financials=financials_ev,
            providers=provider_results
        )

# ── Route Coordinator Function ──

def collect_evidence_package(resolver_result: dict) -> EvidencePackage:
    """Coordinating function used by routes."""
    collector = EvidenceCollector()
    return collector.collect(resolver_result)
