# ─────────────────────────────────────────────────────────────────
# src/committee/orchestrator.py
# ─────────────────────────────────────────────────────────────────
#
# CommitteeOrchestrator invoking the AI Committee Gemini model.
# ─────────────────────────────────────────────────────────────────

import time
import uuid
import json
from datetime import datetime
from typing import List

from src.committee.constants import ReviewStatus, ConflictSeverity, OpinionRecommendation, ReviewerType
from src.committee.models import (
    ConflictObject,
    CommitteeOpinion,
    CommitteeMetadata,
    InvestmentCommitteeReview,
    DecisionOutcome,
    VoteSummary
)
from src.thesis.models import InvestmentThesis
from src.intelligence.models import InvestmentIntelligence
from src.infrastructure.llm.gemini_service import GeminiService
from src.utils.logger import logger

class CommitteeOrchestrator:
    """
    Orchestrates the evaluation of the InvestmentThesis by
    delegating to a single Gemini-driven AI Committee.
    """
    @staticmethod
    def run_review(thesis: InvestmentThesis, intelligence: InvestmentIntelligence) -> InvestmentCommitteeReview:
        start_time = time.perf_counter()
        
        # 1. Prepare Intelligence Summary
        intel_summary_lines = []
        for pillar_name, pillar_result in intelligence.pillars.items():
            intel_summary_lines.append(f"[{pillar_name.upper()}]")
            for finding in pillar_result.findings:
                intel_summary_lines.append(f"- {finding}")
        intel_summary = "\n".join(intel_summary_lines)

        # 2. Prepare Thesis Summary
        thesis_lines = []
        for sec_name, section in thesis.sections.items():
            thesis_lines.append(f"[{sec_name.upper()}]")
            for stmt in section.statements:
                thesis_lines.append(f"- {stmt.finding}")
        thesis_summary = "\n".join(thesis_lines)

        system_prompt = (
            "You are an experienced institutional investment committee responsible for deciding whether a company is investable based on the available evidence.\n"
            "Your responsibility is to evaluate the complete investment case by weighing business quality, financial health, growth potential, valuation, management quality, and risk before reaching a balanced committee decision.\n"
            "You are not writing the investment thesis. The thesis has already been prepared. Your role is to critically evaluate it, challenge its assumptions where necessary, and determine whether the available evidence justifies supporting, questioning, or rejecting the investment.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "3. Evaluate the overall investment case rather than the completeness of the available data.\n"
            "4. Missing valuation metrics, peer comparisons, or secondary information should reduce confidence but should NOT automatically change a positive investment case into HOLD.\n"
            "5. Recommend SUPPORT when the available evidence shows a fundamentally strong business whose strengths clearly outweigh its risks, even if some secondary information is unavailable.\n"
            "6. Recommend HOLD only when the available evidence is genuinely mixed, conflicting, or contains material uncertainty that prevents a confident investment decision.\n"
            "7. Recommend REJECT only when the available evidence demonstrates significant weaknesses that outweigh the company's strengths.\n"
            "8. Clearly distinguish between:\n"
            "   • What is known from the evidence.\n"
            "   • What remains uncertain.\n"
            "   • Why the final committee decision is justified despite those uncertainties.\n"
            "Before making your decision, reason through the following questions internally:\n"
            "• Is this fundamentally a good business?\n"
            "• Are the company's financial fundamentals strong enough to support long-term investment?\n"
            "• Do the company's strengths outweigh its risks?\n"
            "• Are the uncertainties significant enough to change the investment decision, or do they only reduce confidence?\n"
            "• If you were allocating your own capital today, would the available evidence justify investing?\n\n"
            "9. Respond ONLY with a JSON object matching this schema:\n"

            "{\n"
            '  "overallDecision": "SUPPORT" | "HOLD" | "REJECT",\n'
            '  "confidenceLevel": "High" | "Medium" | "Low",\n'
            '  "strongestStrengths": ["Strength 1", "Strength 2"],\n'
            '  "biggestConcerns": ["Concern 1", "Concern 2"],\n'
            '  "disagreements": ["Disagreement 1 (if any)"],\n'
            '  "finalReasoning": "2-4 paragraphs explaining the decision"\n'
            "}"
        )

        user_prompt = (
            f"Company: {thesis.ticker}\n\n"
            f"--- FINANCIAL SUMMARY ---\n"
            f"{intel_summary}\n\n"
            f"--- AI INVESTMENT THESIS ---\n"
            f"{thesis_summary}\n"
        )

        logger.info(f"CommitteeOrchestrator: Invoking Gemini AI Committee for {thesis.ticker}")
        gemini = GeminiService()
        
        llm_output = None
        for attempt in range(2):
            try:
                response_text = gemini.generate_json_response(system_prompt, user_prompt, timeout=25.0)
                llm_output = GeminiService.parse_json_safely(response_text)
                logger.info(f"CommitteeOrchestrator: AI Committee generated successfully on attempt {attempt+1}.")
                break
            except Exception as e:
                logger.error(f"CommitteeOrchestrator: JSON parse failed on attempt {attempt+1}: {str(e)}")
                if attempt == 1:
                    logger.error("CommitteeOrchestrator: Final parse status: FAILED. Using fallback.")
                    break

        if not llm_output:
            llm_output = {
                "overallDecision": "HOLD",
                "confidenceLevel": "Low",
                "strongestStrengths": [],
                "biggestConcerns": ["AI Committee failed to generate a response."],
                "disagreements": [],
                "finalReasoning": "Fallback committee response due to LLM failure."
            }

        # 3. Map to Opinion Recommendation
        raw_rec = llm_output.get("overallDecision", "HOLD").upper().strip()
        if raw_rec == "SUPPORT":
            rec = OpinionRecommendation.SUPPORT
        elif raw_rec == "REJECT":
            rec = OpinionRecommendation.REJECT
        else:
            rec = OpinionRecommendation.QUESTION # Map HOLD to QUESTION for committee opinion

        # We must populate a single CommitteeOpinion to preserve the existing schema
        opinion = CommitteeOpinion(
            reviewerId="AI_COMMITTEE",
            reviewerType=None,
            recommendation=rec,
            recommendationImpact=1.0 if rec == OpinionRecommendation.SUPPORT else -1.0,
            confidence=0.85 if llm_output.get("confidenceLevel") == "High" else 0.5,
            coverageScore=1.0,
            status=ReviewStatus.SUCCESS,
            concerns=llm_output.get("biggestConcerns", []),
            supportingStatements=llm_output.get("strongestStrengths", []),
            conflictingStatements=llm_output.get("disagreements", []),
            assumptions=[],
            missingEvidence=[],
            decisionReferences=[],
            explanationIds=[],
            reviewerVersion="2.0.0",
            rulesVersion="2.0.0",
            executionTimeMs=0.0
        )
        
        opinions = [opinion]
        
        # 4. Map to DecisionOutcome
        support_votes = 1 if rec == OpinionRecommendation.SUPPORT else 0
        reject_votes = 1 if rec == OpinionRecommendation.REJECT else 0
        question_votes = 1 if rec == OpinionRecommendation.QUESTION else 0
        
        decision = DecisionOutcome(
            recommendation=rec,
            decisionReasons=[llm_output.get("finalReasoning", "No reasoning provided.")],
            voteSummary=VoteSummary(
                supportVotes=support_votes,
                questionVotes=question_votes,
                rejectVotes=reject_votes
            )
        )
        
        overall_conf = opinion.confidence
        overall_cov = 1.0
        overall_health = 1.0

        latency = (time.perf_counter() - start_time) * 1000.0
        
        meta = CommitteeMetadata(
            committeeVersion="2.0.0",
            votingVersion="2.0.0",
            compiledAt=datetime.utcnow().isoformat() + "Z",
            latencyMs=round(latency, 2),
            reviewersExecuted=["AI_COMMITTEE"],
            overallCoverage=overall_cov,
            overallHealth=overall_health
        )
        
        return InvestmentCommitteeReview(
            committeeId=str(uuid.uuid4()),
            thesisId=thesis.thesisId,
            intelligenceId=thesis.intelligenceId,
            evidenceId=thesis.evidenceId,
            schemaVersion="1.0.0",
            decisionOutcome=decision,
            overallConfidence=overall_conf,
            opinions=opinions,
            conflicts=[],
            meta=meta
        )
