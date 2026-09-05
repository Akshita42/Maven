# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/bear_agent.py
# ─────────────────────────────────────────────────────────────────
# Dedicated Bear Agent: Formulates the adversarial counter-argument,
# downside valuation stress-test, and operational risk evaluation.
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Any, List, Optional
from src.utils.logger import logger

class BearAgent:
    """
    Specialized AI Agent that constructs the adversarial downside counter-argument.
    """
    
    def generate_bear_case(
        self, 
        ticker: str, 
        intelligence: Any, 
        bull_case: Dict[str, Any],
        sec_insights: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Builds the structured Bear Case challenging the Bull Case on valuation,
        margin risk, macro headwinds, and supply chain concentration.
        """
        logger.info(f"[BearAgent] Generating downside counter-argument for: {ticker}")
        
        bull_thesis = bull_case.get("thesis", "")
        
        bear_case = {
            "agent": "BearAgent",
            "stance": "BEARISH",
            "counterRebuttal": (
                f"While the Bull Agent points to market dominance ('{bull_thesis[:80]}...'), "
                f"the bear case for {ticker.upper()} highlights premium valuation multiples, working capital intensity, "
                f"and sector-wide spending moderation. Any shortfall in quarterly growth rates could trigger multiple compression."
            ),
            "keyRisks": [
                f"Valuation risk: {ticker.upper()} trades at elevated multiples, limiting margin of safety.",
                f"Operational risk: Exposure to supply chain volatility and macroeconomic rate environment.",
                f"Competitive risk: Rapid technology shifts and margin pressure from aggressive market entrants."
            ],
            "downsideStressFactor": f"Valuation compression and growth rate deceleration for {ticker.upper()}."
        }
        
        return bear_case
