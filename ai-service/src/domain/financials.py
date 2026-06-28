# ─────────────────────────────────────────────────────────────────
# src/domain/financials.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain Models for company Financial Statements.
#
# Represents Income Statements, Balance Sheets, Cash Flow Statements,
# derived metrics, trend metrics, validation reports, and quality scores.
# All models are Pydantic v2 frozen/immutable structures.
# ─────────────────────────────────────────────────────────────────

from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict

# ── Provenance Field Envelope ──

class FinancialField(BaseModel):
    """Envelope wrapping a resolved numeric financial value with its provenance trail."""
    model_config = ConfigDict(frozen=True)
    
    value: Optional[int] = None
    source: str
    provider: str
    period: str  # "annual" or "quarterly"
    retrievedAt: str
    confidence: float

# ── Statement Items ──

class IncomeStatement(BaseModel):
    """Canonical domain model for a single period Income Statement."""
    model_config = ConfigDict(frozen=True)
    
    fiscalYear: int
    fiscalQuarter: Optional[int] = None  # None for annual
    periodEndDate: str  # ISO Date String (YYYY-MM-DD)
    currency: str
    
    # Financial metrics (Wrapped in provenance envelopes)
    revenue: Optional[FinancialField] = None
    costOfRevenue: Optional[FinancialField] = None
    grossProfit: Optional[FinancialField] = None
    researchDevelopment: Optional[FinancialField] = None
    sellingGeneralAdministrative: Optional[FinancialField] = None
    operatingExpenses: Optional[FinancialField] = None
    operatingIncome: Optional[FinancialField] = None
    netIncome: Optional[FinancialField] = None

class BalanceSheet(BaseModel):
    """Canonical domain model for a single period Balance Sheet."""
    model_config = ConfigDict(frozen=True)
    
    fiscalYear: int
    fiscalQuarter: Optional[int] = None
    periodEndDate: str
    currency: str
    
    # Financial metrics (Wrapped in provenance envelopes)
    totalAssets: Optional[FinancialField] = None
    totalLiabilities: Optional[FinancialField] = None
    stockholdersEquity: Optional[FinancialField] = None
    cashAndCashEquivalents: Optional[FinancialField] = None
    longTermDebt: Optional[FinancialField] = None
    retainedEarnings: Optional[FinancialField] = None
    currentAssets: Optional[FinancialField] = None
    currentLiabilities: Optional[FinancialField] = None

class CashFlowStatement(BaseModel):
    """Canonical domain model for a single period Cash Flow Statement."""
    model_config = ConfigDict(frozen=True)
    
    fiscalYear: int
    fiscalQuarter: Optional[int] = None
    periodEndDate: str
    currency: str
    
    # Financial metrics (Wrapped in provenance envelopes)
    operatingCashFlow: Optional[FinancialField] = None
    capitalExpenditures: Optional[FinancialField] = None
    freeCashFlow: Optional[FinancialField] = None
    netIncome: Optional[FinancialField] = None

# ── Validation Report ──

class ValidationResult(BaseModel):
    """Represents a single validation assertion result."""
    model_config = ConfigDict(frozen=True)
    
    severity: str  # "INFO" | "WARNING" | "ERROR"
    ruleId: str
    message: str

class ValidationReport(BaseModel):
    """Structured collection of validation checks."""
    model_config = ConfigDict(frozen=True)
    
    overallStatus: str  # "PASSED" | "WARNING" | "FAILED"
    validationScore: float = 1.0
    passedRules: List[str] = []
    failedRules: List[ValidationResult] = []
    warnings: List[ValidationResult] = []
    issues: List[ValidationResult] = []

# ── Statement Coverage ──

class CoverageMetrics(BaseModel):
    """Tracks coverage/completeness percentages individually by statement type."""
    model_config = ConfigDict(frozen=True)
    
    incomeStatementCoverage: float
    balanceSheetCoverage: float
    cashFlowCoverage: float
    overallCoverage: float

# ── Derived Metrics ──

class DerivedFinancialMetrics(BaseModel):
    """Canonical computed financial ratios."""
    model_config = ConfigDict(frozen=True)
    
    grossMargin: Optional[float] = None
    operatingMargin: Optional[float] = None
    netMargin: Optional[float] = None
    freeCashFlowMargin: Optional[float] = None
    returnOnEquity: Optional[float] = None
    returnOnAssets: Optional[float] = None
    debtToEquity: Optional[float] = None
    currentRatio: Optional[float] = None
    cashRatio: Optional[float] = None
    revenueGrowthYoY: Optional[float] = None
    netIncomeGrowthYoY: Optional[float] = None
    freeCashFlowGrowthYoY: Optional[float] = None

class FinancialMetricsPeriod(BaseModel):
    """Wrapper associating derived ratios with a specific fiscal period and data lineage."""
    model_config = ConfigDict(frozen=True)
    
    fiscalYear: int
    fiscalQuarter: Optional[int] = None
    periodEndDate: str
    metrics: DerivedFinancialMetrics
    lineage: Dict[str, List[str]]  # Traceability: maps metric name to raw source property names

# ── Historical Trends ──

class TrendMetric(BaseModel):
    """Represents a computed directional trend with confidence scoring."""
    model_config = ConfigDict(frozen=True)
    
    direction: str  # e.g. "Growing", "Declining", "Improving", "Volatile", "Positive", "Highly Variable"
    confidence: float
    supportingPeriods: int

class FinancialTrends(BaseModel):
    """Historical trends calculated across periods."""
    model_config = ConfigDict(frozen=True)
    
    revenueTrend: TrendMetric
    netIncomeTrend: TrendMetric
    cashFlowTrend: TrendMetric

# ── Diagnostic & Provider Metadata ──

class CompletenessScore(BaseModel):
    """Quality metric representing data completeness for parsed statements."""
    model_config = ConfigDict(frozen=True)
    
    fieldsExpected: int
    fieldsRetrieved: int
    completenessPercentage: float  # Value between 0.0 and 1.0 (e.g. 0.92)

class ProviderMetadata(BaseModel):
    """Diagnostic logs tracing the ingestion details."""
    model_config = ConfigDict(frozen=True)
    
    providerName: str
    providerVersion: str
    retrievalMethod: str
    status: str
    providerHealth: float
    latencyMs: float
    retryCount: int
    retrievedAt: str
    freshnessStatus: str
    ageHours: float
    sourceUrl: str
    recordsRetrieved: int
    recordsExpected: int
    qualityScore: float
    warnings: List[str] = []
    errors: List[str] = []

# ── Unified Company Financials Model ──

class CompanyFinancials(BaseModel):
    """Canonical compiled financials package containing raw data and decoupled analytics."""
    model_config = ConfigDict(frozen=True)
    
    ticker: str
    
    # 1. Raw Statements
    annualIncomeStatements: List[IncomeStatement] = []
    quarterlyIncomeStatements: List[IncomeStatement] = []
    annualBalanceSheets: List[BalanceSheet] = []
    quarterlyBalanceSheets: List[BalanceSheet] = []
    annualCashFlowStatements: List[CashFlowStatement] = []
    quarterlyCashFlowStatements: List[CashFlowStatement] = []
    
    # 2. Decoupled Derived Metrics
    annualDerivedMetrics: List[FinancialMetricsPeriod] = []
    quarterlyDerivedMetrics: List[FinancialMetricsPeriod] = []
    
    # 3. Decoupled Trend Analysis
    trends: Optional[FinancialTrends] = None
    
    # Diagnostics & Quality Scores
    completeness: CompletenessScore
    coverage: CoverageMetrics
    validationReport: ValidationReport
    qualityScore: float
    meta: ProviderMetadata
    retrieved_successfully: bool = False
