# ─────────────────────────────────────────────────────────────────
# src/intelligence/scoring.py
# ─────────────────────────────────────────────────────────────────
#
# Overall Score compilation and Risk Penalty subtraction logic.
# ─────────────────────────────────────────────────────────────────

from typing import Dict
from src.intelligence.models import PillarResult, RiskPenalty
from src.intelligence.constants.scoring_thresholds import PILLAR_WEIGHTS

def compute_overall_score(pillars: Dict[str, PillarResult], penalty: RiskPenalty) -> float:
    """
    Computes overall score (0.0 - 10.0) based on weighted pillar scores
    and subtracting the total risk penalty.
    """
    # Sum weighted scores of the non-risk pillars
    weighted_sum = 0.0
    other_pillars = ["business_quality", "financial_health", "growth", "valuation", "management"]
    
    for key in other_pillars:
        pillar_res = pillars.get(key)
        if pillar_res:
            weighted_sum += pillar_res.rawScore * PILLAR_WEIGHTS[key]
            
    # Normalize by the sum of weights of the other 5 pillars (0.85)
    sum_other_weights = sum(PILLAR_WEIGHTS[k] for k in other_pillars)
    base_score = (weighted_sum / sum_other_weights) if sum_other_weights > 0 else 0.0
    
    # Subtract risk penalty
    overall = base_score - penalty.totalPenalty
    
    return round(max(0.0, min(10.0, overall)), 2)

def compute_overall_confidence(pillars: Dict[str, PillarResult]) -> float:
    """Computes overall confidence as a weighted average of individual pillar confidences."""
    weighted_conf = 0.0
    total_weight = 0.0
    
    for key, pillar_res in pillars.items():
        weight = PILLAR_WEIGHTS.get(key, 0.0)
        weighted_conf += pillar_res.confidence * weight
        total_weight += weight
        
    return round(weighted_conf / total_weight, 4) if total_weight > 0 else 1.0
