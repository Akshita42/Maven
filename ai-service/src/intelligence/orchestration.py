# ─────────────────────────────────────────────────────────────────
# src/intelligence/orchestration.py
# ─────────────────────────────────────────────────────────────────
#
# Simple orchestration coordinator to assemble context and run analyzers.
# ─────────────────────────────────────────────────────────────────

import time
import uuid
from datetime import datetime
from typing import Dict, List
from src.utils.logger import logger

from src.domain.contracts.evidence import EvidencePackage
from src.intelligence.models import (
    ReasoningContext,
    ValidationSummary,
    CoverageSummary,
    PillarResult,
    RiskPenalty,
    PipelineMetadata,
    ExecutionMetadata,
    InvestmentIntelligence
)

from src.intelligence.analyzers.business_quality import BusinessQualityAnalyzer
from src.intelligence.analyzers.financial_health import FinancialHealthAnalyzer
from src.intelligence.analyzers.growth import GrowthAnalyzer
from src.intelligence.analyzers.valuation import ValuationAnalyzer
from src.intelligence.analyzers.risk import RiskAnalyzer
from src.intelligence.analyzers.management import ManagementAnalyzer

from src.intelligence.scoring import compute_overall_score, compute_overall_confidence

class IntelligenceService:
    """
    Orchestration service coordinating structural context building and executing
    the six deterministic analyzers. Strictly read-only relative to evidence.
    """
    def __init__(self):
        self.analyzers = {
            "business_quality": BusinessQualityAnalyzer(),
            "financial_health": FinancialHealthAnalyzer(),
            "growth": GrowthAnalyzer(),
            "valuation": ValuationAnalyzer(),
            "risk": RiskAnalyzer(),
            "management": ManagementAnalyzer()
        }

    def compile_intelligence(self, evidence: EvidencePackage) -> InvestmentIntelligence:
        start_time = time.perf_counter()
        
        ticker_val = evidence.companyProfile.ticker.value if evidence.companyProfile and evidence.companyProfile.ticker else "Unknown"
        logger.info(f"IntelligenceService: Orchestrating analysis for symbol '{ticker_val}'...")
        
        # 1. Build Reasoning Context summaries
        provider_health = {}
        provider_quality = {}
        for k, p in evidence.providers.items():
            provider_health[k] = p.providerHealth
            provider_quality[k] = p.qualityScore
            
        financials = evidence.financials.value if evidence.financials else None
        
        # Validation Report Summary
        val_rep = evidence.validationReport
        if not val_rep and financials:
            val_rep = financials.validationReport
            
        val_summary = ValidationSummary(
            overallStatus=val_rep.overallStatus if val_rep else "PASSED",
            validationScore=val_rep.validationScore if val_rep else 1.0,
            failedRulesCount=len(val_rep.failedRules) if val_rep else 0,
            warningsCount=len(val_rep.warnings) if val_rep else 0
        )
        
        # Coverage Summary
        cov = financials.coverage if financials else None
        cov_summary = CoverageSummary(
            incomeStatementCoverage=cov.incomeStatementCoverage if cov else 1.0,
            balanceSheetCoverage=cov.balanceSheetCoverage if cov else 1.0,
            cashFlowCoverage=cov.cashFlowCoverage if cov else 1.0,
            overallCoverage=cov.overallCoverage if cov else 1.0
        )
        
        # Missing evidence compilation
        missing = []
        if not financials:
            missing.append("financial_statements")
        if not evidence.companyProfile or not evidence.companyProfile.companyName.value:
            missing.append("company_profile")
        if not evidence.marketData or not evidence.marketData.currentPrice.value:
            missing.append("market_data")
            
        # Context warnings
        warnings = []
        if val_rep:
            for issue in val_rep.issues:
                warnings.append(issue.message)
                
        context = ReasoningContext(
            evidence=evidence,
            providerHealthSummary=provider_health,
            validationSummary=val_summary,
            qualitySummary=provider_quality,
            coverageSummary=cov_summary,
            missingEvidenceSummary=missing,
            globalWarnings=warnings
        )
        
        # 2. Sequentially execute analyzers
        pillars: Dict[str, PillarResult] = {}
        executed = []
        
        for name, analyzer in self.analyzers.items():
            try:
                logger.info(f"IntelligenceService: Executing {analyzer.__class__.__name__}...")
                pillars[name] = analyzer.analyze(context)
                executed.append(analyzer.__class__.__name__)
            except Exception as e:
                logger.error(f"IntelligenceService: {analyzer.__class__.__name__} failed: {str(e)}")
                # Failures are gracefully handled where possible, but core pipeline errors out if critical
                raise RuntimeError(f"Intelligence compilation crashed in {name} analyzer: {str(e)}")
                
        # 3. Compute Risk Penalty
        risk_analyzer: RiskAnalyzer = self.analyzers["risk"]
        penalty = risk_analyzer.calculate_penalty(context)
        
        # 4. Compute overall score & confidence
        overall_score = compute_overall_score(pillars, penalty)
        overall_conf = compute_overall_confidence(pillars)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        exec_meta = ExecutionMetadata(
            compiledAt=datetime.utcnow().isoformat() + "Z",
            latencyMs=round(latency, 2),
            analyzersExecuted=executed
        )
        
        # Assemble final InvestmentIntelligence package
        return InvestmentIntelligence(
            schemaVersion="1.0.0",
            intelligenceId=str(uuid.uuid4()),
            evidenceId=evidence.evidenceId,
            ticker=ticker_val,
            overallScore=overall_score,
            overallConfidence=overall_conf,
            pillars=pillars,
            riskPenalty=penalty,
            pipelineMeta=PipelineMetadata(),
            meta=exec_meta
        )
