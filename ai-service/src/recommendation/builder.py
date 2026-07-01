import uuid
import json
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
from src.infrastructure.llm.gemini_service import GeminiService
from src.utils.logger import logger

class RecommendationBuilder:
    """
    Builds the final immutable InvestmentRecommendation using AI synthesis,
    while preserving deterministic confidence scores and schema mappings.
    """
    
    @staticmethod
    def build(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        critique: InvestmentCritique
    ) -> InvestmentRecommendation:
        
        # 1. Deterministic Confidence Score Computation (PRESERVED)
        robustness = critique.robustnessSummary.stabilityIndex
        base_confidence = 0.5
        
        support_count = sum(1 for op in review.opinions if op.recommendation == OpinionRecommendation.SUPPORT)
        reject_count = sum(1 for op in review.opinions if op.recommendation == OpinionRecommendation.REJECT)
        total_opinions = max(len(review.opinions), 1)
        agreement_ratio = max(support_count, reject_count) / total_opinions
        base_confidence += (agreement_ratio * 0.20)
        base_confidence += (robustness * 0.15)
        
        audit_count = len(critique.coverageAudits)
        audit_penalty = min(audit_count * 0.05, 0.20)
        base_confidence -= audit_penalty
        
        confidence = max(0.1, min(0.99, base_confidence + 0.14))
        
        # 2. Gather context for AI Synthesis
        thesis_statements = [stmt.finding for section in thesis.sections.values() for stmt in section.statements]
        committee_opinions = [{"reviewer": op.reviewerId, "stance": op.recommendation.value, "concerns": op.concerns, "supporting": op.supportingStatements} for op in review.opinions]
        if review.decisionOutcome and review.decisionOutcome.decisionReasons:
            committee_opinions.append({"reviewer": "COMMITTEE_SUMMARY", "reasoning": review.decisionOutcome.decisionReasons})
        
        system_prompt = (
            "You are a professional equity research analyst writing the final investment note after an investment committee has already reached its decision.\n"
            "Your responsibility is NOT to decide whether the investment should be BUY, HOLD, or SELL. The committee has already made that decision.\n"
            "Your responsibility is to explain and justify the committee's decision in a clear, balanced, and professional investment note for the reader.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. Start with a clear investment conclusion before explaining the details.\n"
            "2. Build a logical investment case by weighing both the strengths and the risks instead of listing facts.\n"
            "3. Explain why the evidence leads to BUY, HOLD, or SELL. Connect business quality, financial health, growth, valuation, and risks into one coherent story.\n"
            "4. Focus on what the evidence means for an investor rather than repeating financial metrics.\n"
            "5. If important evidence is missing, clearly explain how that uncertainty affects the recommendation instead of making assumptions.\n"
            "6. Keep the tone concise, professional, objective, and similar to an equity research report.\n"
            "7. NEVER hallucinate facts or invent metrics. Use only the provided evidence, thesis, and committee output.\n"
            "8. Preserve the committee's final recommendation exactly as provided. Do not generate a different recommendation.\n\n"
            "Respond ONLY with a JSON object matching this schema:\n"
            "{\n"
            '  "recommendation": "BUY",\n'
            '  "investment_thesis": "2-3 concise paragraphs explaining the overarching thesis and reasoning like a professional investment note.",\n'
            '  "why_this_recommendation": ["Bullet point 1", "Bullet point 2"],\n'
            '  "key_risks": ["Risk 1", "Risk 2"],\n'
            '  "key_assumptions": ["Assumption 1", "Assumption 2"],\n'
            '  "what_could_change_this_recommendation": ["Catalyst 1", "Catalyst 2"]\n'
            "}"
        )
        
        from src.services.company_service import resolve_company_metadata
        company_meta = resolve_company_metadata(thesis.ticker)
        
        user_prompt = (
            f"Company Name: {company_meta.companyName or thesis.ticker}\n"
            f"Symbol: {thesis.ticker}\n"
            f"Sector: {company_meta.sector or 'Unknown'}\n"
            f"Industry: {company_meta.industry or 'Unknown'}\n\n"
            f"Confidence Score: {confidence:.2f} (1.0 = Max Confidence)\n\n"
            f"AI Generated Investment Thesis:\n{json.dumps(thesis_statements, indent=2)}\n\n"
            f"Committee Votes:\n{json.dumps(committee_opinions, indent=2)}\n"
        )
        
        logger.info(f"RecommendationBuilder: Calling Gemini for final synthesis of {thesis.ticker}")
        gemini = GeminiService()
        
        llm_output = None
        for attempt in range(2):
            try:
                response_text = gemini.generate_json_response(system_prompt, user_prompt, timeout=25.0)
                llm_output = GeminiService.parse_json_safely(response_text)
                logger.info(f"RecommendationBuilder: JSON extraction succeeded on attempt {attempt+1}. Retry used: {attempt > 0}. Final status: SUCCESS")
                break
            except Exception as e:
                logger.error(f"RecommendationBuilder: JSON parse failed on attempt {attempt+1}: {str(e)}")
                if attempt == 1:
                    logger.error("RecommendationBuilder: Final parse status: FAILED. Falling back to deterministic pipeline.")
                    break
                    
        if not llm_output:
            llm_output = {
                "recommendation": "HOLD",
                "investment_thesis": "This recommendation is based on the deterministic financial analysis because an AI synthesis was unavailable.",
                "why_this_recommendation": ["Information currently unavailable."],
                "key_risks": [],
                "key_assumptions": [],
                "what_could_change_this_recommendation": []
            }
            
        # 3. Map LLM Output to Deterministic Enums and Schemas
        committee_decision = review.decisionOutcome.recommendation

        if committee_decision == OpinionRecommendation.SUPPORT:
            stance = InvestmentStance.BUY
        elif committee_decision == OpinionRecommendation.REJECT:
            stance = InvestmentStance.SELL
        else:
            stance = InvestmentStance.HOLD
            
        conviction = ConvictionLevel.MEDIUM
        if robustness >= 0.80 and confidence >= 0.80:
            conviction = ConvictionLevel.HIGH
        elif robustness < 0.50 or confidence < 0.50:
            conviction = ConvictionLevel.LOW
            
        horizon = TimeHorizon.LONG_TERM
        
        if stance == InvestmentStance.BUY:
            investment_outlook = "Bullish"
            suggested_actions = ["New Investor → BUY", "Existing Holder → HOLD", "Consider expanding position"]
        elif stance == InvestmentStance.HOLD:
            investment_outlook = "Neutral"
            suggested_actions = ["New Investor → WAIT", "Existing Holder → HOLD", "Monitor for catalysts"]
        else:
            investment_outlook = "Bearish"
            suggested_actions = ["New Investor → AVOID", "Existing Holder → Consider reducing position"]
            
        # 4. Map text fields to report model
        key_positives = llm_output.get("why_this_recommendation", [])
        key_risks = llm_output.get("key_risks", [])
        committee_reasons = [llm_output.get("investment_thesis", "No thesis provided.")]
        critique_highlights = llm_output.get("key_assumptions", [])
        
        monitoring_items = []
        catalysts = []
        for change_item in llm_output.get("what_could_change_this_recommendation", []):
            catalysts.append(RecommendationCatalyst(description=change_item, impactDirection="UNKNOWN"))
            monitoring_items.append(MonitoringItem(description=change_item, triggerThreshold="Monitor", sourceReviewerId="AI Synthesis"))
            
        meta = RecommendationMetadata(
            thesisVersion=thesis.meta.schemaVersion,
            committeeVersion=review.meta.committeeVersion,
            critiqueVersion=critique.meta.critiqueVersion,
            compiledAt=datetime.utcnow().isoformat() + "Z",
            status=RecommendationStatus.SUCCESS
        )

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
        
        return rec

