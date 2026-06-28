# ─────────────────────────────────────────────────────────────────
# src/intelligence/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable Domain Models for the Investment Intelligence Layer.
# Enforces strict schemas and types using Pydantic v2.
# ─────────────────────────────────────────────────────────────────

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.constants.enums import (
    AnalyzerStatus,
    Rating,
    RuleSeverity,
    RuleStatus,
    ValidationStatus
)

class EvidenceReference(BaseModel):
    """Structured location pointer within the EvidencePackage."""
    model_config = ConfigDict(frozen=True)
    
    section: str  # e.g., "financials", "companyProfile", "marketData", "news"
    collection: str  # e.g., "annualDerivedMetrics", "quarterlyBalanceSheets", "none"
    field: str  # e.g., "operatingMargin", "totalAssets", "currentPrice"
    period: Optional[str] = None  # e.g., "FY2025" or None
    provider: str  # e.g., "Yahoo Finance Timeseries API" or "Yahoo Profile Scraper"

class DecisionTrace(BaseModel):
    """Represents a single trace of a calculation logic step."""
    model_config = ConfigDict(frozen=True)
    
    rule: str
    observedValue: str  # Convert value to string representation for stability
    threshold: str
    result: RuleStatus
    scoreImpact: float
    evidenceReference: EvidenceReference

class RuleResult(BaseModel):
    """Summarized execution status of a single analyzer rule."""
    model_config = ConfigDict(frozen=True)
    
    ruleId: str  # e.g., "FH-001"
    ruleName: str
    severity: RuleSeverity
    status: RuleStatus
    scoreImpact: float

class AnalyzerMetadata(BaseModel):
    """Diagnostic tracking for each individual analyzer execution."""
    model_config = ConfigDict(frozen=True)
    
    analyzerName: str
    analyzerVersion: str
    rulesVersion: str
    executionTimeMs: float
    rulesExecuted: int
    coverageScore: float
    status: AnalyzerStatus

class ValidationSummary(BaseModel):
    """Structured summary of the validation report checks."""
    model_config = ConfigDict(frozen=True)
    
    overallStatus: ValidationStatus
    validationScore: float
    failedRulesCount: int
    warningsCount: int

class CoverageSummary(BaseModel):
    """Structured summary of statement completeness."""
    model_config = ConfigDict(frozen=True)
    
    incomeStatementCoverage: float
    balanceSheetCoverage: float
    cashFlowCoverage: float
    overallCoverage: float

class ReasoningContext(BaseModel):
    """The standard execution parameter encapsulating the entire reasoning state."""
    model_config = ConfigDict(frozen=True)
    
    evidence: EvidencePackage
    providerHealthSummary: Dict[str, float]
    validationSummary: ValidationSummary
    qualitySummary: Dict[str, float]
    coverageSummary: CoverageSummary
    missingEvidenceSummary: List[str]
    globalWarnings: List[str]

class PillarResult(BaseModel):
    """The structured output package of each analyzer."""
    model_config = ConfigDict(frozen=True)
    
    pillar: str
    rawScore: float  # scale of 0.0 to 10.0
    weightedScore: float
    rating: Rating
    confidence: float  # scale of 0.0 to 1.0
    coverageScore: float
    strengths: List[str]
    weaknesses: List[str]
    missingEvidence: List[str]
    supportingEvidence: List[str]
    evidenceUsed: List[str]
    assumptions: List[str]
    contradictions: List[str]
    limitations: List[str]
    findings: List[str]  # Short, deterministic statements only (no text paragraphs)
    explanationIds: List[str]  # stable identifiers like ["FH-001", "FH-002"]
    ruleResults: List[RuleResult]
    decisionTraces: List[DecisionTrace]
    meta: AnalyzerMetadata

class RiskPenalty(BaseModel):
    """Structured breakdown of the risk score deductions."""
    model_config = ConfigDict(frozen=True)
    
    validationPenalty: float
    coveragePenalty: float
    financialPenalty: float
    providerPenalty: float
    totalPenalty: float

class PipelineMetadata(BaseModel):
    """Version and execution metadata for the intelligence scoring run."""
    model_config = ConfigDict(frozen=True)
    
    pipelineVersion: str = "1.0.0"
    buildVersion: str = "1.0.0"
    generatedBy: str = "Maven Intelligence Orchestrator"

class ExecutionMetadata(BaseModel):
    """Observability metadata for the compile task."""
    model_config = ConfigDict(frozen=True)
    
    compiledAt: str
    latencyMs: float
    analyzersExecuted: List[str]

class InvestmentIntelligence(BaseModel):
    """The final immutable API contract package."""
    model_config = ConfigDict(frozen=True)
    
    schemaVersion: str = "1.0.0"
    intelligenceId: str  # UUID
    evidenceId: str  # Traceability link
    ticker: str
    overallScore: float  # scale of 0.0 to 10.0 (overall weighted score minus risk penalty)
    overallConfidence: float
    pillars: Dict[str, PillarResult]
    riskPenalty: RiskPenalty
    pipelineMeta: PipelineMetadata
    meta: ExecutionMetadata
