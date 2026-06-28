# ─────────────────────────────────────────────────────────────────
# src/committee/voting.py
# ─────────────────────────────────────────────────────────────────
#
# Deterministic Voting Engine to evaluate opinions and output decisions.
# ─────────────────────────────────────────────────────────────────

from typing import List
from src.committee.constants import OpinionRecommendation
from src.committee.models import CommitteeOpinion, DecisionOutcome, VoteSummary

class VotingEngine:
    """
    Stateless evaluator that aggregates individual reviewer opinions, counts votes,
    and returns a structured DecisionOutcome.
    """
    @staticmethod
    def compute_outcome(opinions: List[CommitteeOpinion]) -> DecisionOutcome:
        support_votes = 0
        question_votes = 0
        reject_votes = 0
        
        reasons: List[str] = []
        
        for op in opinions:
            rec = op.recommendation
            # Append individual reviewer voting record
            reasons.append(f"{op.reviewerId} reviewer voted {rec.value}.")
            
            if rec == OpinionRecommendation.SUPPORT:
                support_votes += 1
            elif rec == OpinionRecommendation.QUESTION:
                question_votes += 1
            elif rec == OpinionRecommendation.REJECT:
                reject_votes += 1
                
        summary = VoteSummary(
            supportVotes=support_votes,
            questionVotes=question_votes,
            rejectVotes=reject_votes
        )
        
        # Apply deterministic voting outcome rules
        if reject_votes >= 2:
            recommendation = OpinionRecommendation.REJECT
            reasons.append(f"Committee rejection triggered: {reject_votes} REJECT votes received.")
        elif support_votes >= 3 and reject_votes == 0:
            recommendation = OpinionRecommendation.SUPPORT
            reasons.append(f"Committee support consensus reached: {support_votes} SUPPORT votes, 0 REJECT votes.")
        else:
            recommendation = OpinionRecommendation.QUESTION
            reasons.append(f"Committee question status: Vote count does not satisfy support consensus. SUPPORT={support_votes}, QUESTION={question_votes}, REJECT={reject_votes}.")
            
        return DecisionOutcome(
            recommendation=recommendation,
            decisionReasons=reasons,
            voteSummary=summary
        )
