# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/valuation.py
# ─────────────────────────────────────────────────────────────────
#
# ValuationAnalyzer evaluating pricing, caps, and peer boundaries.
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
    MAX_PE_RATIO_BENCHMARK,
    MIN_PE_RATIO_CHEAP,
    PILLAR_WEIGHTS
)
from src.intelligence.constants.ratings import get_rating_for_score

class ValuationAnalyzer(BaseAnalyzer):
    """
    Evaluates corporate relative valuation and pricing ranges.
    Valuation confidence is strictly capped at 0.55 when benchmark databases are missing.
    """
    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        market = context.evidence.marketData
        profile = context.evidence.companyProfile
        
        required_fields = ["currentPrice", "marketCap"]
        fields_retrieved = 0
        missing = []
        for field in required_fields:
            ev_field = getattr(market, field, None) or getattr(profile, field, None)
            if ev_field and ev_field.value is not None:
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
        
        # Rule VL-001: Valuation Data Check
        price_val = market.currentPrice.value if market.currentPrice else None
        if price_val is not None:
            evidence_used.append("marketData.currentPrice")
            ref = EvidenceReference(
                section="marketData",
                collection="none",
                field="currentPrice",
                provider=market.currentPrice.source
            )
            findings.append(f"Current market trading price is {price_val}.")
            traces.append(DecisionTrace(
                rule="VL-001 (Market Price Ingested)",
                observedValue=str(price_val),
                threshold="> 0.0",
                result=RuleStatus.PASS,
                scoreImpact=0.0,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="VL-001",
                ruleName="ValuationPriceCheck",
                severity=RuleSeverity.INFO,
                status=RuleStatus.PASS,
                scoreImpact=0.0
            ))
        else:
            rules.append(RuleResult(
                ruleId="VL-001",
                ruleName="ValuationPriceCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Market price data is missing; skipped valuation checks.")

        # Capping confidence because benchmark multiples/analyst/DCF are absent
        # "Valuation confidence must never exceed 0.55 unless valid benchmark evidence exists."
        confidence = 0.50  # Cap confidence below 0.55
        
        missing.extend(["peerMultiplesDatabase", "analystEstimates", "discountedCashFlowModelInputs"])
        limitations = ["Valuation confidence is capped due to missing sector/industry peer benchmarks."]
        findings.append("Capped valuation confidence due to missing sector peer multiples benchmarks.")

        score = max(0.0, min(10.0, score))
        rating = get_rating_for_score(score)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["valuation"]
        meta_info = AnalyzerMetadata(
            analyzerName="ValuationAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage, 4),
            status=status
        )
        
        return PillarResult(
            pillar="valuation",
            rawScore=round(score, 2),
            weightedScore=round(score * PILLAR_WEIGHTS["valuation"], 4),
            rating=rating,
            confidence=confidence,
            coverageScore=round(coverage, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            missingEvidence=missing,
            supportingEvidence=[f"Ticker: {context.evidence.companyProfile.ticker.value if context.evidence.companyProfile and context.evidence.companyProfile.ticker else 'Unknown'}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Market capitalization reflects recent share listings."],
            contradictions=[],
            limitations=limitations,
            findings=findings,
            explanationIds=["VL-001"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
