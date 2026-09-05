# ─────────────────────────────────────────────────────────────────
# src/committee/reviewers/bull_agent.py
# ─────────────────────────────────────────────────────────────────
# Dedicated Bull Agent: Synthesizes the bullish investment case,
# market moat, growth drivers, and upside financial tailwinds.
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Any, List, Optional
from src.utils.logger import logger

class BullAgent:
    """
    Specialized AI Agent that constructs the bullish upside thesis.
    """
    
    def generate_bull_case(
        self, 
        ticker: str, 
        intelligence: Any, 
        sec_insights: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Builds the structured Bull Case containing key drivers, growth vectors,
        and target valuation catalysts.
        """
        logger.info(f"[BullAgent] Generating upside investment case for: {ticker}")
        
        # Extract qualitative snippets if available
        sec_highlights = []
        if sec_insights:
            for ins in sec_insights[:2]:
                sec_highlights.append(ins.get("content", ""))
                
        sec_text = " ".join(sec_highlights) if sec_highlights else "Demonstrates strong market position and capital allocation discipline."
        
        bull_case = {
            "agent": "BullAgent",
            "stance": "BULLISH",
            "thesis": (
                f"The upside thesis for {ticker.upper()} is anchored by category leadership, pricing power, "
                f"and robust return on equity. Key growth drivers include product innovation, operating leverage expansion, "
                f"and sustained customer retention. {sec_text}"
            ),
            "keyDrivers": [
                f"High-moat market dominance and pricing authority for {ticker.upper()}.",
                f"Defensible operating margins and compounding free cash flow.",
                f"Strategic expansion in high-ROI growth verticals."
            ],
            "upsideTargetCatalyst": f"Accelerated earnings beat and market share expansion for {ticker.upper()}."
        }
        
        return bull_case
