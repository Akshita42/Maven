# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/growth.py
# ─────────────────────────────────────────────────────────────────
#
# GrowthAnalyzer evaluating YoY growths and long-term trends.
# ─────────────────────────────────────────────────────────────────

import time
from typing import List
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
    MIN_REVENUE_GROWTH_EXCELLENT,
    MIN_REVENUE_GROWTH_STRONG,
    MIN_REVENUE_GROWTH_AVERAGE,
    MIN_NET_INCOME_GROWTH_STRONG,
    PILLAR_WEIGHTS
)
from src.intelligence.constants.ratings import get_rating_for_score

class GrowthAnalyzer(BaseAnalyzer):
    """
    Evaluates revenue, net income growth velocities, and historical trend directions.
    """
    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        financials = context.evidence.financials.value
        
        # Check evidence availability
        if not financials or not financials.annualDerivedMetrics:
            meta_info = AnalyzerMetadata(
                analyzerName="GrowthAnalyzer",
                analyzerVersion=ANALYZER_VERSIONS["growth"]["analyzerVersion"],
                rulesVersion=ANALYZER_VERSIONS["growth"]["rulesVersion"],
                executionTimeMs=0.0,
                rulesExecuted=0,
                coverageScore=0.0,
                status=AnalyzerStatus.FAILED
            )
            return PillarResult(
                pillar="growth",
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
                limitations=["No growth history available."],
                findings=["No growth history ingested."],
                explanationIds=[],
                ruleResults=[],
                decisionTraces=[],
                meta=meta_info
            )

        latest_metrics_period = financials.annualDerivedMetrics[0]
        metrics = latest_metrics_period.metrics
        p_date = latest_metrics_period.periodEndDate
        provider = context.evidence.financials.source if context.evidence.financials else "Yahoo Finance Timeseries API"
        
        required_fields = ["revenueGrowthYoY", "netIncomeGrowthYoY"]
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
        
        def make_ref(field_name: str) -> EvidenceReference:
            evidence_used.append(f"financials.annualDerivedMetrics.{field_name}")
            return EvidenceReference(
                section="financials",
                collection="annualDerivedMetrics",
                field=field_name,
                period=p_date,
                provider=provider
            )

        # Rule GR-001: Revenue Growth Check
        rev_growth = metrics.revenueGrowthYoY
        if rev_growth is not None:
            ref = make_ref("revenueGrowthYoY")
            if rev_growth >= MIN_REVENUE_GROWTH_EXCELLENT:
                impact = 1.5
                result_status = RuleStatus.PASS
                strengths.append(f"High-velocity revenue expansion: {rev_growth:.2%}")
                findings.append(f"Revenue growth is high ({rev_growth:.2%}).")
            elif rev_growth >= MIN_REVENUE_GROWTH_STRONG:
                impact = 0.5
                result_status = RuleStatus.PASS
                findings.append(f"Revenue growth is solid ({rev_growth:.2%}).")
            elif rev_growth <= MIN_REVENUE_GROWTH_AVERAGE:
                impact = -1.0
                result_status = RuleStatus.FAIL
                weaknesses.append(f"Sub-optimal or negative growth: {rev_growth:.2%}")
                findings.append(f"Revenue growth is weak ({rev_growth:.2%}).")
            else:
                impact = 0.0
                result_status = RuleStatus.PASS
                findings.append(f"Revenue growth is average ({rev_growth:.2%}).")
                
            traces.append(DecisionTrace(
                rule="GR-001 (Revenue Growth)",
                observedValue=f"{rev_growth:.4f}",
                threshold=f">= {MIN_REVENUE_GROWTH_EXCELLENT:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="GR-001",
                ruleName="RevenueGrowthYoYCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="GR-001",
                ruleName="RevenueGrowthYoYCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Revenue growth metrics are missing; skipped YoY check.")

        # Rule GR-002: Net Income Growth Check
        ni_growth = metrics.netIncomeGrowthYoY
        if ni_growth is not None:
            ref = make_ref("netIncomeGrowthYoY")
            if ni_growth >= MIN_NET_INCOME_GROWTH_STRONG:
                impact = 1.0
                result_status = RuleStatus.PASS
                strengths.append(f"Strong profitability growth: {ni_growth:.2%}")
                findings.append(f"Net income growth is solid ({ni_growth:.2%}).")
            elif ni_growth < 0.0:
                impact = -0.5
                result_status = RuleStatus.WARNING
                weaknesses.append(f"Earnings contraction: {ni_growth:.2%}")
                findings.append(f"Net income growth is negative ({ni_growth:.2%}).")
            else:
                impact = 0.0
                result_status = RuleStatus.PASS
                findings.append(f"Net income growth is stable ({ni_growth:.2%}).")
                
            traces.append(DecisionTrace(
                rule="GR-002 (Net Income Growth)",
                observedValue=f"{ni_growth:.4f}",
                threshold=f">= {MIN_NET_INCOME_GROWTH_STRONG:.2f}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="GR-002",
                ruleName="NetIncomeGrowthYoYCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="GR-002",
                ruleName="NetIncomeGrowthYoYCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Net income growth metrics are missing; skipped check.")

        # Rule GR-003: Long-term Revenue Trend Check
        trends = financials.trends
        if trends and trends.revenueTrend:
            evidence_used.append("financials.trends.revenueTrend")
            ref = EvidenceReference(
                section="financials",
                collection="trends",
                field="revenueTrend",
                provider=provider
            )
            trend_val = trends.revenueTrend.direction
            if trend_val == "Growing":
                impact = 1.0
                result_status = RuleStatus.PASS
                strengths.append("Persistent long-term historical revenue growth trend.")
                findings.append("Long-term revenue trend vector is classified as Growing.")
            elif trend_val == "Declining":
                impact = -1.5
                result_status = RuleStatus.FAIL
                weaknesses.append("Long-term historical revenue decline trend.")
                findings.append("Long-term revenue trend vector is classified as Declining.")
            else:
                impact = 0.0
                result_status = RuleStatus.PASS
                findings.append(f"Long-term revenue trend vector is {trend_val}.")
                
            traces.append(DecisionTrace(
                rule="GR-003 (Revenue Trend Direction)",
                observedValue=str(trend_val),
                threshold="Growing",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="GR-003",
                ruleName="RevenueTrendDirectionCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            rules.append(RuleResult(
                ruleId="GR-003",
                ruleName="RevenueTrendDirectionCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Revenue trend vectors are missing; skipped trend checks.")

        score = max(0.0, min(10.0, score))
        rating = get_rating_for_score(score)
        
        confidence = round(0.5 + (0.5 * coverage), 4)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["growth"]
        meta_info = AnalyzerMetadata(
            analyzerName="GrowthAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage, 4),
            status=status
        )
        
        return PillarResult(
            pillar="growth",
            rawScore=round(score, 2),
            weightedScore=round(score * PILLAR_WEIGHTS["growth"], 4),
            rating=rating,
            confidence=confidence,
            coverageScore=round(coverage, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            missingEvidence=missing,
            supportingEvidence=[f"Latest Ingestion Period: {p_date}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Historical YoY comparisons reflect consistent internal audit periods."],
            contradictions=[],
            limitations=["YoY growth ratios do not account for external macroeconomic cycles."],
            findings=findings,
            explanationIds=["GR-001", "GR-002", "GR-003"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
