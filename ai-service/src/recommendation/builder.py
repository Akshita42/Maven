# ─────────────────────────────────────────────────────────────────
# src/recommendation/builder.py
# ─────────────────────────────────────────────────────────────────
#
# Deterministic Recommendation Builder.
# Synthesizes inputs without AI or external calls.
# ─────────────────────────────────────────────────────────────────

import uuid
from datetime import datetime
from src.recommendation.constants import (
    InvestmentStance, 
    TimeHorizon, 
    ConvictionLevel, 
    RecommendationStatus
)
from src.recommendation.models import (
    InvestmentRecommendation,
    RecommendationMetadata,
    MonitoringItem,
    RecommendationCatalyst
)
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.committee.constants import OpinionRecommendation
from src.critique.models import InvestmentCritique

class RecommendationBuilder:
    """
    Builds the final immutable InvestmentRecommendation from prior layers.
    """
    
    @staticmethod
    def build(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        critique: InvestmentCritique
    ) -> InvestmentRecommendation:
        
        # 1. Deterministic Stance Mapping
        decision = review.decisionOutcome.recommendation
        robustness = critique.robustnessSummary.stabilityIndex
        
        # Deterministic Confidence Score Computation
        base_confidence = 0.5
        
        # 1. Committee Agreement (Max +0.20)
        support_count = sum(1 for op in review.opinions if op.recommendation == OpinionRecommendation.SUPPORT)
        reject_count = sum(1 for op in review.opinions if op.recommendation == OpinionRecommendation.REJECT)
        total_opinions = max(len(review.opinions), 1)
        agreement_ratio = max(support_count, reject_count) / total_opinions
        base_confidence += (agreement_ratio * 0.20)
        
        # 2. Critique Robustness (Max +0.15)
        base_confidence += (robustness * 0.15)
        
        # 3. Evidence Completeness / Missing Data Penalty (Max -0.20)
        audit_count = len(critique.coverageAudits)
        audit_penalty = min(audit_count * 0.05, 0.20)
        base_confidence -= audit_penalty
        
        # Normalize and set final confidence
        confidence = max(0.1, min(0.99, base_confidence + 0.14))
        
        stance = InvestmentStance.HOLD
        if decision == OpinionRecommendation.SUPPORT:
            if robustness >= 0.80 and confidence >= 0.80:
                stance = InvestmentStance.BUY
                if robustness >= 0.90 and confidence >= 0.90:
                    stance = InvestmentStance.STRONG_BUY
            elif robustness < 0.80:
                stance = InvestmentStance.HOLD
            else:
                stance = InvestmentStance.BUY
        elif decision == OpinionRecommendation.QUESTION:
            stance = InvestmentStance.HOLD
        elif decision == OpinionRecommendation.REJECT:
            if robustness >= 0.80 and confidence >= 0.80:
                stance = InvestmentStance.STRONG_SELL
            else:
                stance = InvestmentStance.SELL

        # 2. Conviction Level
        conviction = ConvictionLevel.MEDIUM
        if robustness >= 0.80 and confidence >= 0.80:
            conviction = ConvictionLevel.HIGH
        elif robustness < 0.50 or confidence < 0.50:
            conviction = ConvictionLevel.LOW
            
        # 3. Time Horizon (Default to Long Term, could map from metrics if available)
        horizon = TimeHorizon.LONG_TERM
            
        # 4. Extract Deterministic Highlights and Map IDs to readable strings
        statement_lookup = {}
        for section in thesis.sections.values():
            for stmt in section.statements:
                statement_lookup[stmt.statementId] = stmt.finding

        key_positives = []
        for op in review.opinions:
            if op.recommendation == OpinionRecommendation.SUPPORT:
                for stmt_id in op.supportingStatements:
                    val = statement_lookup.get(stmt_id, stmt_id)
                    key_positives.append(val)
        key_positives = list(dict.fromkeys(key_positives))[:5] # Deduplicate, max 5
        
        key_risks = []
        for op in review.opinions:
            for risk_id in op.concerns:
                # Filter out system diagnostics from being presented as investment risks
                risk_lower = risk_id.lower()
                if "database" in risk_lower or "validation" in risk_lower or "coverage" in risk_lower or "missing" in risk_lower:
                    continue
                    
                val = statement_lookup.get(risk_id, risk_id)
                key_risks.append(val)
        
        # Fallbacks for ultra-safe companies where committee finds 0 explicit concerns
        if not key_risks:
            # 1. Critique Vulnerabilities
            for vuln in critique.actionableVulnerabilities.invalidatingAssumptions:
                key_risks.append(f"Vulnerability: {vuln.description}")
            for bias in critique.biasEvaluations:
                key_risks.append(f"Bias Risk: {bias.description}")
                
        if not key_risks:
            # 2. Valuation Concerns (e.g. capped confidence)
            val_sec = thesis.sections.get("valuation")
            if val_sec:
                for stmt in val_sec.statements:
                    finding = stmt.finding.lower()
                    if "capped" in finding or "missing" in finding or "high" in finding or "overvalued" in finding:
                        key_risks.append(stmt.finding)
                        
        if not key_risks:
            # 3. Any missing evidence warnings
            for op in review.opinions:
                if op.missingEvidence:
                    key_risks.append(f"Information Gap: Missing evidence for {op.reviewerId.lower()} analysis.")
                    
        key_risks = list(dict.fromkeys(key_risks))[:5]
        
        if not key_risks:
            key_risks.append("No significant risks were identified from the available evidence.")
        
        committee_reasons = list(review.decisionOutcome.decisionReasons)
        
        critique_highlights = []
        for vuln in critique.actionableVulnerabilities.invalidatingAssumptions:
            critique_highlights.append(f"Assumption Vulnerability: {vuln.description}")
        for bias in critique.biasEvaluations:
            critique_highlights.append(f"Bias Identified: {bias.description}")
            
        # 5. Extract Monitoring Items & Catalysts
        monitoring_items = []
        for audit in critique.coverageAudits:
            monitoring_items.append(MonitoringItem(
                description=audit.description,
                triggerThreshold="Resolution of missing evidence",
                sourceReviewerId=audit.targetPillar
            ))
            
        catalysts = []
        for sim in critique.robustnessAnalysis.scenarios:
            if not sim.isRobust:
                catalysts.append(RecommendationCatalyst(
                    description=f"Trigger event matching stress scenario: {sim.name}",
                    impactDirection="NEGATIVE"
                ))
        if stance in (InvestmentStance.BUY, InvestmentStance.STRONG_BUY):
            catalysts.append(RecommendationCatalyst(
                description="Earnings beat driving positive multiple expansion",
                impactDirection="POSITIVE"
            ))

        meta = RecommendationMetadata(
            thesisVersion=thesis.meta.schemaVersion,
            committeeVersion=review.meta.committeeVersion,
            critiqueVersion=critique.meta.critiqueVersion,
            compiledAt=datetime.utcnow().isoformat() + "Z",
            status=RecommendationStatus.SUCCESS
        )

        if stance in (InvestmentStance.BUY, InvestmentStance.STRONG_BUY):
            investment_outlook = "Bullish"
            suggested_actions = ["New Investor → BUY", "Existing Holder → HOLD", "Consider expanding position"]
        elif stance == InvestmentStance.HOLD:
            investment_outlook = "Neutral"
            suggested_actions = ["New Investor → WAIT", "Existing Holder → HOLD", "Monitor for catalysts"]
        else:
            investment_outlook = "Bearish"
            suggested_actions = ["New Investor → AVOID", "Existing Holder → Consider reducing position"]

        rec = InvestmentRecommendation(
            recommendationId=str(uuid.uuid4()),
            thesisId=thesis.thesisId,
            committeeReviewId=review.committeeId,
            critiqueId=critique.critiqueId,
            intelligenceId=thesis.intelligenceId,
            evidenceId=thesis.evidenceId,
            schemaVersion="1.0.0",
            stance=stance,
            investmentOutlook=investment_outlook,
            suggestedActions=suggested_actions,
            horizon=horizon,
            conviction=conviction,
            confidenceScore=round(confidence, 4),
            keyPositives=key_positives,
            keyRisks=key_risks,
            committeeReasons=committee_reasons,
            critiqueHighlights=critique_highlights,
            monitoringItems=monitoring_items,
            catalysts=catalysts,
            meta=meta
        )
        
        print("EXIT RecommendationBuilder.build")
        return rec
