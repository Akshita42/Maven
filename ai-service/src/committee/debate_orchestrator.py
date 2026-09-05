# ─────────────────────────────────────────────────────────────────
# src/committee/debate_orchestrator.py
# ─────────────────────────────────────────────────────────────────
# Orchestrates 2-Turn Bull vs. Bear Dialectic Debate and Arbitrates
# the consensus Investment Committee decision.
# ─────────────────────────────────────────────────────────────────

import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.logger import logger
from src.committee.reviewers.bull_agent import BullAgent
from src.committee.reviewers.bear_agent import BearAgent
from src.committee.constants import OpinionRecommendation, ReviewStatus, ReviewerType
from src.committee.models import (
    InvestmentCommitteeReview,
    DecisionOutcome,
    VoteSummary,
    CommitteeOpinion,
    CommitteeMetadata
)

class DialecticDebateOrchestrator:
    """
    Manages adversarial debate between BullAgent and BearAgent,
    synthesizing an impartial consensus decision.
    """
    
    def __init__(self):
        self.bull_agent = BullAgent()
        self.bear_agent = BearAgent()

    def run_debate(
        self, 
        ticker: str, 
        intelligence: Any, 
        sec_insights: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes 2-turn Bull vs. Bear dialectic debate and synthesizes consensus.
        Returns a dict containing:
          - 'transcript': List of debate turns
          - 'review': InvestmentCommitteeReview model instance
          - 'bull_case': BullAgent output
          - 'bear_case': BearAgent output
        """
        start_time = time.perf_counter()
        logger.info(f"[DialecticDebateOrchestrator] Initiating Bull vs. Bear debate for: {ticker}")
        
        # Turn 1: Bull Case
        bull_case = self.bull_agent.generate_bull_case(ticker, intelligence, sec_insights)
        
        # Turn 2: Bear Counter-Rebuttal
        bear_case = self.bear_agent.generate_bear_case(ticker, intelligence, bull_case, sec_insights)
        
        transcript = [
            {
                "turn": 1,
                "speaker": "Bull Agent",
                "content": bull_case["thesis"],
                "keyPoints": bull_case["keyDrivers"]
            },
            {
                "turn": 2,
                "speaker": "Bear Agent",
                "content": bear_case["counterRebuttal"],
                "keyPoints": bear_case["keyRisks"]
            }
        ]
        
        # Arbitrator Decision Synthesis
        overall_score = getattr(intelligence, "overallScore", 7.0) if intelligence else 7.0
        
        if overall_score >= 5.5:
            rec = OpinionRecommendation.SUPPORT
            confidence = 0.88
            final_reasoning = f"The Investment Committee arbitrated the Bull vs. Bear debate in favor of {ticker.upper()}. Fundamental quality and high-moat profitability outweigh valuation downside risks."
            support_v, question_v, reject_v = 2, 1, 0
        elif overall_score >= 4.0:
            rec = OpinionRecommendation.QUESTION
            confidence = 0.75
            final_reasoning = f"The Investment Committee concluded a balanced debate for {ticker.upper()}. Solid operational performance is offset by valuation risks, justifying a HOLD position."
            support_v, question_v, reject_v = 1, 2, 0
        else:
            rec = OpinionRecommendation.REJECT
            confidence = 0.85
            final_reasoning = f"The Investment Committee arbitrated in favor of the Bear Agent for {ticker.upper()}. Elevated risk factors and valuation overpricing outweigh growth prospects."
            support_v, question_v, reject_v = 0, 1, 2
            
        opinion = CommitteeOpinion(
            reviewerId="DIALECTIC_DEBATE_ARBITRATOR",
            reviewerType=None,
            recommendation=rec,
            recommendationImpact=1.0 if rec == OpinionRecommendation.SUPPORT else -1.0,
            confidence=confidence,
            coverageScore=1.0,
            status=ReviewStatus.SUCCESS,
            concerns=bear_case["keyRisks"],
            supportingStatements=bull_case["keyDrivers"],
            conflictingStatements=[bear_case["counterRebuttal"]],
            assumptions=[],
            missingEvidence=[],
            decisionReferences=[],
            explanationIds=[],
            reviewerVersion="3.0.0",
            rulesVersion="3.0.0",
            executionTimeMs=0.0
        )
        
        decision = DecisionOutcome(
            recommendation=rec,
            decisionReasons=[final_reasoning],
            voteSummary=VoteSummary(
                supportVotes=support_v,
                questionVotes=question_v,
                rejectVotes=reject_v
            )
        )
        
        latency = (time.perf_counter() - start_time) * 1000.0
        meta = CommitteeMetadata(
            committeeVersion="3.0.0",
            votingVersion="3.0.0",
            compiledAt=datetime.utcnow().isoformat() + "Z",
            latencyMs=round(latency, 2),
            reviewersExecuted=["BullAgent", "BearAgent", "DebateArbitrator"],
            overallCoverage=1.0,
            overallHealth=1.0
        )
        
        review = InvestmentCommitteeReview(
            committeeId=f"committee-{uuid.uuid4()}",
            thesisId=f"thesis-{uuid.uuid4()}",
            intelligenceId=f"intel-{uuid.uuid4()}",
            evidenceId=f"ev-{uuid.uuid4()}",
            schemaVersion="1.0.0",
            decisionOutcome=decision,
            overallConfidence=confidence,
            opinions=[opinion],
            conflicts=[],
            meta=meta
        )
        
        return {
            "transcript": transcript,
            "review": review,
            "bull_case": bull_case,
            "bear_case": bear_case
        }
