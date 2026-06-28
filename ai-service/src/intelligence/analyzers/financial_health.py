# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/financial_health.py
# ─────────────────────────────────────────────────────────────────
#
# FinancialHealthAnalyzer evaluating solvency, margins, and ratios.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List, Optional
from src.intelligence.interfaces import BaseAnalyzer
from src.intelligence.models import (
    PillarResult,
    ReasoningContext,
    DecisionTrace,
    RuleResult,
    EvidenceReference,
    AnalyzerMetadata
)
from src.intelligence.constants.enums import (
    AnalyzerStatus,
    Rating,
    RuleSeverity,
    RuleStatus
)
from src.intelligence.constants.analyzer_versions import ANALYZER_VERSIONS
from src.intelligence.constants.scoring_thresholds import (
    MIN_OPERATING_MARGIN_EXCELLENT,
    MIN_OPERATING_MARGIN_STRONG,
    MIN_OPERATING_MARGIN_AVERAGE,
    MIN_ROE_STRONG,
    MIN_ROE_AVERAGE,
    MAX_DEBT_TO_EQUITY_CRITICAL,
    MAX_DEBT_TO_EQUITY_WARNING,
    MIN_CURRENT_RATIO_SAFE,
    MIN_CURRENT_RATIO_WARNING,
    PILLAR_WEIGHTS
)
from src.intelligence.constants.ratings import get_rating_for_score

class FinancialHealthAnalyzer(BaseAnalyzer):
    """
    Evaluates corporate solvency, margins, and liquidity ratios using
    the most recent annual derived metrics.
    """
    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        financials = context.evidence.financials.value
        
        # Check evidence availability
        if not financials or not financials.annualDerivedMetrics:
            meta_info = AnalyzerMetadata(
                analyzerName="FinancialHealthAnalyzer",
                analyzerVersion=ANALYZER_VERSIONS["financial_health"]["analyzerVersion"],
                rulesVersion=ANALYZER_VERSIONS["financial_health"]["rulesVersion"],
                executionTimeMs=0.0,
                rulesExecuted=0,
                coverageScore=0.0,
                status=AnalyzerStatus.FAILED
            )
            return PillarResult(
                pillar="financial_health",
                rawScore=0.0,
                weightedScore=0.0,
                rating=Rating.CRITICAL,
                confidence=0.0,
                coverageScore=0.0,
                strengths=[],
                weaknesses=["Missing all financials evidence."],
                missingEvidence=["annualDerivedMetrics"],
                supportingEvidence=[],
                evidenceUsed=[],
                assumptions=[],
                contradictions=[],
                limitations=["No financial statements parsed."],
                findings=["No financial statements ingested."],
                explanationIds=[],
                ruleResults=[],
                decisionTraces=[],
                meta=meta_info
            )

        # Get latest annual derived metrics period
        latest_metrics_period = financials.annualDerivedMetrics[0]
        metrics = latest_metrics_period.metrics
        p_date = latest_metrics_period.periodEndDate
        provider = context.evidence.financials.source if context.evidence.financials else "Yahoo Finance Timeseries API"
        
        # Coverage calculation
        required_fields = ["operatingMargin", "returnOnEquity", "debtToEquity", "currentRatio"]
        fields_retrieved = 0
        missing = []
        for field in required_fields:
            if getattr(metrics, field, None) is not None:
                fields_retrieved += 1
            else:
                missing.append(field)
                
        coverage = fields_retrieved / len(required_fields)
        status = AnalyzerStatus.SUCCESS
        if coverage == 0.0:
            status = AnalyzerStatus.FAILED
        elif coverage < 1.0:
            status = AnalyzerStatus.PARTIAL
            
        traces: List[DecisionTrace] = []
        rules: List[RuleResult] = []
        strengths: List[str] = []
        weaknesses: List[str] = []
        findings: List[str] = []
        evidence_used: List[str] = []
        
        score = 5.0
        
        # Helper to construct evidence ref
        def make_ref(field_name: str) -> EvidenceReference:
            evidence_used.append(f"financials.annualDerivedMetrics.{field_name}")
            return EvidenceReference(
                section="financials",
                collection="annualDerivedMetrics",
                field=field_name,
                period=p_date,
                provider=provider
            )

        # Rule FH-001: Operating Margin Check
        op_margin = metrics.operatingMargin
        if op_margin is not None:
            ref = make_ref("operatingMargin")
            if op_margin >= MIN_OPERATING_MARGIN_EXCELLENT:
                impact = 1.5
                result_status = RuleStatus.PASS
                strengths.append(f"Outstanding operating margin: {op_margin:.2%}")
                findings.append(f"Operating margin is high ({op_margin:.2%}).")
            elif op_margin >= MIN_OPERATING_MARGIN_STRONG:
                impact = 0.5
                result_status = RuleStatus.PASS
                findings.append(f"Operating margin is solid ({op_margin:.2%}).")
            elif op_margin < MIN_OPERATING_MARGIN_AVERAGE:
                impact = -1.0
                result_status = RuleStatus.FAIL
                weaknesses.append(f"Compressed operating margin: {op_margin:.2%}")
                findings.append(f"Operating margin is compressed ({op_margin:.2%}).")
            else:
                impact = 0.0
                result_status = RuleStatus.PASS
                findings.append(f"Operating margin is average ({op_margin:.2%}).")
                
            traces.append(DecisionTrace(
                rule="FH-001 (Operating Margin)",
                observedValue=f"{op_margin:.4f}",
                threshold=f">= {MIN_OPERATING_MARGIN_EXCELLENT:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="FH-001",
                ruleName="OperatingMarginCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="FH-001",
                ruleName="OperatingMarginCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Operating margin is missing; skipped profitability check.")

        # Rule FH-002: Return on Equity (ROE) Check
        roe = metrics.returnOnEquity
        if roe is not None:
            ref = make_ref("returnOnEquity")
            if roe >= MIN_ROE_STRONG:
                impact = 1.5
                result_status = RuleStatus.PASS
                strengths.append(f"Highly efficient capital return (ROE: {roe:.2%})")
                findings.append(f"Return on Equity is efficient ({roe:.2%}).")
            elif roe >= MIN_ROE_AVERAGE:
                impact = 0.5
                result_status = RuleStatus.PASS
                findings.append(f"Return on Equity is stable ({roe:.2%}).")
            else:
                impact = -0.5
                result_status = RuleStatus.WARNING
                weaknesses.append(f"Sub-optimal capital efficiency (ROE: {roe:.2%})")
                findings.append(f"Return on Equity is sub-optimal ({roe:.2%}).")
                
            traces.append(DecisionTrace(
                rule="FH-002 (ROE Check)",
                observedValue=f"{roe:.4f}",
                threshold=f">= {MIN_ROE_STRONG:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="FH-002",
                ruleName="ReturnOnEquityCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="FH-002",
                ruleName="ReturnOnEquityCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("ROE metrics are missing; skipped equity efficiency check.")

        # Rule FH-003: Debt to Equity (D/E) Check
        de = metrics.debtToEquity
        if de is not None:
            ref = make_ref("debtToEquity")
            if de <= MAX_DEBT_TO_EQUITY_WARNING:
                impact = 1.0
                result_status = RuleStatus.PASS
                strengths.append(f"Conservative leverage profile (D/E: {de:.2f})")
                findings.append(f"Debt-to-Equity is conservative ({de:.2f}).")
            elif de >= MAX_DEBT_TO_EQUITY_CRITICAL:
                impact = -2.0
                result_status = RuleStatus.FAIL
                weaknesses.append(f"Excessive solvency risk detected (D/E: {de:.2f})")
                findings.append(f"Debt-to-Equity is excessive ({de:.2f}), presenting high solvency risk.")
            else:
                impact = -0.5
                result_status = RuleStatus.WARNING
                weaknesses.append(f"Moderate debt levels (D/E: {de:.2f})")
                findings.append(f"Debt-to-Equity is moderate ({de:.2f}).")
                
            traces.append(DecisionTrace(
                rule="FH-003 (Debt to Equity)",
                observedValue=f"{de:.4f}",
                threshold=f"<= {MAX_DEBT_TO_EQUITY_WARNING:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="FH-003",
                ruleName="DebtToEquityCheck",
                severity=RuleSeverity.ERROR if de >= MAX_DEBT_TO_EQUITY_CRITICAL else RuleSeverity.WARNING,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="FH-003",
                ruleName="DebtToEquityCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Solvency metrics are missing; skipped leverage check.")

        # Rule FH-004: Current Ratio Check
        cr = metrics.currentRatio
        if cr is not None:
            ref = make_ref("currentRatio")
            if cr >= MIN_CURRENT_RATIO_SAFE:
                impact = 1.0
                result_status = RuleStatus.PASS
                strengths.append(f"Healthy liquid buffer (Current Ratio: {cr:.2f})")
                findings.append(f"Current ratio is healthy ({cr:.2f}).")
            elif cr < MIN_CURRENT_RATIO_WARNING:
                impact = -1.5
                result_status = RuleStatus.FAIL
                weaknesses.append(f"Inadequate liquid buffer (Current Ratio: {cr:.2f})")
                findings.append(f"Current ratio is inadequate ({cr:.2f}), indicating liquidity risk.")
            else:
                impact = -0.5
                result_status = RuleStatus.WARNING
                findings.append(f"Current ratio is borderline ({cr:.2f}).")
                
            traces.append(DecisionTrace(
                rule="FH-004 (Current Ratio)",
                observedValue=f"{cr:.4f}",
                threshold=f">= {MIN_CURRENT_RATIO_SAFE:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="FH-004",
                ruleName="CurrentRatioCheck",
                severity=RuleSeverity.ERROR if cr < MIN_CURRENT_RATIO_WARNING else RuleSeverity.WARNING,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="FH-004",
                ruleName="CurrentRatioCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Liquidity metrics are missing; skipped current ratio check.")

        score = max(0.0, min(10.0, score))
        rating = get_rating_for_score(score)
        
        # Calculate confidence based on coverage
        confidence = round(0.5 + (0.5 * coverage), 4)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["financial_health"]
        meta_info = AnalyzerMetadata(
            analyzerName="FinancialHealthAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage, 4),
            status=status
        )
        
        return PillarResult(
            pillar="financial_health",
            rawScore=round(score, 2),
            weightedScore=round(score * PILLAR_WEIGHTS["financial_health"], 4),
            rating=rating,
            confidence=confidence,
            coverageScore=round(coverage, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            missingEvidence=missing,
            supportingEvidence=[f"Fiscal Year: {latest_metrics_period.fiscalYear}", f"Ending Date: {p_date}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Operating margin and ROE calculations reflect standard GAAP/IFRS figures."],
            contradictions=[],
            limitations=["Leverage analysis depends on equity valuations which can fluctuate."],
            findings=findings,
            explanationIds=["FH-001", "FH-002", "FH-003", "FH-004"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
