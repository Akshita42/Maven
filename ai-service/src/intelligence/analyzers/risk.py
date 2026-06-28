# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/risk.py
# ─────────────────────────────────────────────────────────────────
#
# RiskAnalyzer implementing a penalty-based scoring system.
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
    AnalyzerMetadata,
    RiskPenalty
)
from src.intelligence.constants.enums import (
    AnalyzerStatus,
    Rating,
    RuleSeverity,
    RuleStatus
)
from src.intelligence.constants.analyzer_versions import ANALYZER_VERSIONS
from src.intelligence.constants.scoring_thresholds import PILLAR_WEIGHTS
from src.intelligence.constants.ratings import get_rating_for_score

class RiskAnalyzer(BaseAnalyzer):
    """
    Evaluates corporate and operational risks using validation reports,
    data coverage anomalies, and provider health. Calculates structured RiskPenalty.
    """
    def calculate_penalty(self, context: ReasoningContext) -> RiskPenalty:
        """Computes the structured RiskPenalty parameters."""
        # 1. Validation Penalty
        val_summary = context.validationSummary
        val_penalty = (val_summary.failedRulesCount * 1.5) + (val_summary.warningsCount * 0.5)
        
        # 2. Coverage Penalty
        cov_summary = context.coverageSummary
        cov_penalty = round((1.0 - cov_summary.overallCoverage) * 3.0, 4)
        
        # 3. Provider Penalty
        failed_providers = sum(1 for h in context.providerHealthSummary.values() if h < 0.5)
        provider_penalty = failed_providers * 1.0
        
        # 4. Financial Consistency Penalty (Volatility/anomalies)
        financial_penalty = 0.0
        financials = context.evidence.financials.value
        if financials and financials.trends:
            if financials.trends.netIncomeTrend.direction == "Volatile":
                financial_penalty += 0.5
            if financials.trends.revenueTrend.direction == "Declining":
                financial_penalty += 1.0

        total_penalty = round(val_penalty + cov_penalty + provider_penalty + financial_penalty, 4)
        
        return RiskPenalty(
            validationPenalty=round(val_penalty, 4),
            coveragePenalty=round(cov_penalty, 4),
            financialPenalty=round(financial_penalty, 4),
            providerPenalty=round(provider_penalty, 4),
            totalPenalty=total_penalty
        )

    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        penalty = self.calculate_penalty(context)
        
        traces: List[DecisionTrace] = []
        rules: List[RuleResult] = []
        strengths: List[str] = []
        weaknesses: List[str] = []
        findings: List[str] = []
        evidence_used: List[str] = []
        
        # Risk analyzer score starts at 10.0 and is penalized
        raw_score = max(0.0, 10.0 - penalty.totalPenalty)
        rating = get_rating_for_score(raw_score)
        
        # Trace Validation Penalty
        if penalty.validationPenalty > 0.0:
            evidence_used.append("validationSummary.failedRulesCount")
            ref = EvidenceReference(
                section="financials",
                collection="validationReport",
                field="overallStatus",
                provider="Evidence Validation Engine"
            )
            weaknesses.append(f"Validation reports triggered {context.validationSummary.failedRulesCount} failures.")
            findings.append(f"Validation rules failed check, inducing validation penalty of -{penalty.validationPenalty:.2f}.")
            traces.append(DecisionTrace(
                rule="RK-001 (Validation Failures Penalty)",
                observedValue=str(context.validationSummary.failedRulesCount),
                threshold="0",
                result=RuleStatus.FAIL,
                scoreImpact=-penalty.validationPenalty,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="RK-001",
                ruleName="ValidationFailuresPenalty",
                severity=RuleSeverity.ERROR,
                status=RuleStatus.FAIL,
                scoreImpact=-penalty.validationPenalty
            ))
        else:
            findings.append("No validation rule failures detected.")
            rules.append(RuleResult(
                ruleId="RK-001",
                ruleName="ValidationFailuresPenalty",
                severity=RuleSeverity.INFO,
                status=RuleStatus.PASS,
                scoreImpact=0.0
            ))

        # Trace Coverage Penalty
        if penalty.coveragePenalty > 0.0:
            evidence_used.append("coverageSummary.overallCoverage")
            ref = EvidenceReference(
                section="financials",
                collection="coverage",
                field="overallCoverage",
                provider="Evidence Coverage Service"
            )
            weaknesses.append(f"Incomplete statements coverage: {context.coverageSummary.overallCoverage:.2%}")
            findings.append(f"Missing statement fields, inducing coverage penalty of -{penalty.coveragePenalty:.2f}.")
            traces.append(DecisionTrace(
                rule="RK-002 (Coverage Completeness Penalty)",
                observedValue=f"{context.coverageSummary.overallCoverage:.4f}",
                threshold="1.0",
                result=RuleStatus.WARNING,
                scoreImpact=-penalty.coveragePenalty,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="RK-002",
                ruleName="CoverageCompletenessPenalty",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.WARNING,
                scoreImpact=-penalty.coveragePenalty
            ))
        else:
            findings.append("Statement fields are 100% complete.")
            rules.append(RuleResult(
                ruleId="RK-002",
                ruleName="CoverageCompletenessPenalty",
                severity=RuleSeverity.INFO,
                status=RuleStatus.PASS,
                scoreImpact=0.0
            ))

        coverage_score = context.coverageSummary.overallCoverage
        status = AnalyzerStatus.SUCCESS
        if coverage_score == 0.0:
            status = AnalyzerStatus.FAILED
        elif coverage_score < 1.0:
            status = AnalyzerStatus.PARTIAL
            
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["risk"]
        meta_info = AnalyzerMetadata(
            analyzerName="RiskAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage_score, 4),
            status=status
        )
        
        return PillarResult(
            pillar="risk",
            rawScore=round(raw_score, 2),
            weightedScore=round(raw_score * PILLAR_WEIGHTS["risk"], 4),
            rating=rating,
            confidence=1.0,  # Penalty math itself is certain
            coverageScore=round(coverage_score, 4),
            strengths=[] if penalty.totalPenalty > 0 else ["No operational or validation risk factors identified."],
            weaknesses=weaknesses,
            missingEvidence=context.missingEvidenceSummary,
            supportingEvidence=[f"Total Penalty Incurred: -{penalty.totalPenalty:.2f}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Solvency risk weights assume correct timeseries date synchronization."],
            contradictions=[],
            limitations=["Does not evaluate geopolitical or foreign exchange conversion risks."],
            findings=findings,
            explanationIds=["RK-001", "RK-002"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
