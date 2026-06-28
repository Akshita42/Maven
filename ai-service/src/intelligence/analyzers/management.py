# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/management.py
# ─────────────────────────────────────────────────────────────────
#
# ManagementAnalyzer evaluating governance and structural exchanges.
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
from src.intelligence.constants.scoring_thresholds import PILLAR_WEIGHTS
from src.intelligence.constants.ratings import get_rating_for_score

class ManagementAnalyzer(BaseAnalyzer):
    """
    Evaluates corporate governance safety using exchange listing and registry data.
    Does not hallucinate board details.
    """
    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        profile = context.evidence.companyProfile
        
        required_fields = ["exchange"]
        fields_retrieved = 0
        missing = []
        for field in required_fields:
            ev_field = getattr(profile, field, None)
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
        
        # Rule MG-001: Listing Exchange Governance Check
        exchange_val = profile.exchange.value if profile.exchange else None
        if exchange_val:
            evidence_used.append("companyProfile.exchange")
            ref = EvidenceReference(
                section="companyProfile",
                collection="none",
                field="exchange",
                provider=profile.exchange.source
            )
            
            safe_exchanges = ["NASDAQ", "NYSE", "NEW YORK STOCK EXCHANGE", "NASDAQ GLOBAL SELECT MARKET"]
            if str(exchange_val).upper() in safe_exchanges:
                impact = 1.5
                score += impact
                result_status = RuleStatus.PASS
                strengths.append(f"Listed on tier-1 regulated exchange: {exchange_val}")
                findings.append(f"Exchange is tier-1 regulated ({exchange_val}).")
            else:
                impact = 0.0
                result_status = RuleStatus.PASS
                findings.append(f"Exchange regulatory requirements are standard ({exchange_val}).")
                
            traces.append(DecisionTrace(
                rule="MG-001 (Exchange Listing Safety)",
                observedValue=str(exchange_val),
                threshold="in NASDAQ/NYSE",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="MG-001",
                ruleName="ExchangeListingSafetyCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            missing.append("exchange")
            rules.append(RuleResult(
                ruleId="MG-001",
                ruleName="ExchangeListingSafetyCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Exchange metadata is missing; skipped listing safety check.")

        # Cap confidence because qualitative management indicators are missing
        confidence = 0.50
        missing.extend(["boardOfDirectorsRegistry", "compensationCommitteeLogs"])
        findings.append("Capped governance confidence due to missing qualitative management board files.")

        score = max(0.0, min(10.0, score))
        rating = get_rating_for_score(score)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["management"]
        meta_info = AnalyzerMetadata(
            analyzerName="ManagementAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage, 4),
            status=status
        )
        
        return PillarResult(
            pillar="management",
            rawScore=round(score, 2),
            weightedScore=round(score * PILLAR_WEIGHTS["management"], 4),
            rating=rating,
            confidence=confidence,
            coverageScore=round(coverage, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            missingEvidence=missing,
            supportingEvidence=[f"Exchange: {exchange_val or 'Unknown'}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Exchange listing rules imply active corporate filings compliance."],
            contradictions=[],
            limitations=["Exchange compliance does not measure internal executive compensation policies."],
            findings=findings,
            explanationIds=["MG-001"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
