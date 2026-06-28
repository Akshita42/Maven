# ─────────────────────────────────────────────────────────────────
# src/intelligence/analyzers/business_quality.py
# ─────────────────────────────────────────────────────────────────
#
# BusinessQualityAnalyzer evaluating sector, labor footprint, and moat.
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
    MIN_EMPLOYEES_LARGE_SCALE,
    MIN_EMPLOYEES_MID_SCALE,
    PILLAR_WEIGHTS
)
from src.intelligence.constants.ratings import get_rating_for_score

class BusinessQualityAnalyzer(BaseAnalyzer):
    """
    Evaluates corporate business quality based on sector, employee footprint,
    and available profile metadata. Deterministic and explainable.
    """
    def analyze(self, context: ReasoningContext) -> PillarResult:
        start_time = time.perf_counter()
        
        profile = context.evidence.companyProfile
        ticker_field = context.evidence.companyProfile.ticker if context.evidence.companyProfile else None
        
        # 1. Check evidence availability and compute coverage
        required_fields = ["sector", "industry", "employees", "businessSummary"]
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
        explanation_ids: List[str] = []
        strengths: List[str] = []
        weaknesses: List[str] = []
        findings: List[str] = []
        assumptions: List[str] = []
        evidence_used: List[str] = []
        
        # Base score
        score = 5.0
        
        # Rule BQ-001: Sector Moat Check
        sector_val = profile.sector.value if profile.sector else None
        if sector_val:
            evidence_used.append("companyProfile.sector")
            ref = EvidenceReference(
                section="companyProfile",
                collection="none",
                field="sector",
                provider=profile.sector.source
            )
            
            # High premium moated sectors
            moated_sectors = ["Technology", "Healthcare", "Financial Services"]
            if sector_val in moated_sectors:
                impact = 1.5
                score += impact
                traces.append(DecisionTrace(
                    rule="BQ-001 (Moated Sector)",
                    observedValue=str(sector_val),
                    threshold="in " + str(moated_sectors),
                    result=RuleStatus.PASS,
                    scoreImpact=impact,
                    evidenceReference=ref
                ))
                rules.append(RuleResult(
                    ruleId="BQ-001",
                    ruleName="SectorMoatCheck",
                    severity=RuleSeverity.INFO,
                    status=RuleStatus.PASS,
                    scoreImpact=impact
                ))
                strengths.append(f"Operates in high-moat sector: {sector_val}")
                findings.append(f"Sector is classified as high-moat ({sector_val}).")
            else:
                traces.append(DecisionTrace(
                    rule="BQ-001 (Standard Sector)",
                    observedValue=str(sector_val),
                    threshold="in " + str(moated_sectors),
                    result=RuleStatus.PASS,
                    scoreImpact=0.0,
                    evidenceReference=ref
                ))
                rules.append(RuleResult(
                    ruleId="BQ-001",
                    ruleName="SectorMoatCheck",
                    severity=RuleSeverity.INFO,
                    status=RuleStatus.PASS,
                    scoreImpact=0.0
                ))
                findings.append(f"Sector is classified as standard-moat ({sector_val}).")
        else:
            missing.append("sector")
            rules.append(RuleResult(
                ruleId="BQ-001",
                ruleName="SectorMoatCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Sector data is missing; skipped sector moat check.")

        # Rule BQ-002: Employee Scale Check
        employees_val = profile.employees.value if profile.employees else None
        if employees_val is not None:
            evidence_used.append("companyProfile.employees")
            ref = EvidenceReference(
                section="companyProfile",
                collection="none",
                field="employees",
                provider=profile.employees.source
            )
            
            if employees_val >= MIN_EMPLOYEES_LARGE_SCALE:
                impact = 1.5
                score += impact
                result_status = RuleStatus.PASS
                strengths.append("Large employee footprint indicates organizational scale.")
                findings.append(f"Employees count is {employees_val}, denoting large enterprise scale.")
            elif employees_val >= MIN_EMPLOYEES_MID_SCALE:
                impact = 0.5
                score += impact
                result_status = RuleStatus.PASS
                findings.append(f"Employees count is {employees_val}, denoting medium enterprise scale.")
            else:
                impact = -0.5
                score += impact
                result_status = RuleStatus.WARNING
                weaknesses.append("Small employee base may indicate high key-person risk.")
                findings.append(f"Employees count is {employees_val}, denoting small enterprise scale.")
                
            traces.append(DecisionTrace(
                rule="BQ-002 (Employee Scale)",
                observedValue=str(employees_val),
                threshold=f">= {MIN_EMPLOYEES_LARGE_SCALE}",
                result=result_status,
                scoreImpact=impact,
                evidenceReference=ref
            ))
            rules.append(RuleResult(
                ruleId="BQ-002",
                ruleName="EmployeeScaleCheck",
                severity=RuleSeverity.INFO,
                status=result_status,
                scoreImpact=impact
            ))
        else:
            missing.append("employees")
            rules.append(RuleResult(
                ruleId="BQ-002",
                ruleName="EmployeeScaleCheck",
                severity=RuleSeverity.WARNING,
                status=RuleStatus.SKIPPED,
                scoreImpact=0.0
            ))
            findings.append("Employee metrics are missing; skipped scale checks.")

        score = max(0.0, min(10.0, score))
        rating = get_rating_for_score(score)
        
        # Calculate confidence based on coverage
        confidence = round(0.5 + (0.5 * coverage), 4)
        
        latency = (time.perf_counter() - start_time) * 1000.0
        
        version_info = ANALYZER_VERSIONS["business_quality"]
        meta_info = AnalyzerMetadata(
            analyzerName="BusinessQualityAnalyzer",
            analyzerVersion=version_info["analyzerVersion"],
            rulesVersion=version_info["rulesVersion"],
            executionTimeMs=round(latency, 2),
            rulesExecuted=len(rules),
            coverageScore=round(coverage, 4),
            status=status
        )
        
        return PillarResult(
            pillar="business_quality",
            rawScore=round(score, 2),
            weightedScore=round(score * PILLAR_WEIGHTS["business_quality"], 4),
            rating=rating,
            confidence=confidence,
            coverageScore=round(coverage, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            missingEvidence=missing,
            supportingEvidence=[f"Ticker: {ticker_field.value if ticker_field else 'Unknown'}"],
            evidenceUsed=list(set(evidence_used)),
            assumptions=["Sector categorization maps to standard Yahoo industry designations."],
            contradictions=[],
            limitations=["Qualitative moat strength cannot be fully measured by employee scale alone."],
            findings=findings,
            explanationIds=["BQ-001", "BQ-002"],
            ruleResults=rules,
            decisionTraces=traces,
            meta=meta_info
        )
