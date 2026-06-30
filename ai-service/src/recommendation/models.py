# ─────────────────────────────────────────────────────────────────
# src/recommendation/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable domain models for the final Investment Recommendation.
# ─────────────────────────────────────────────────────────────────

from typing import List
from pydantic import BaseModel, ConfigDict, Field
from src.recommendation.constants import InvestmentStance, TimeHorizon, ConvictionLevel, RecommendationStatus

class MonitoringItem(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str
    triggerThreshold: str
    sourceReviewerId: str

class RecommendationCatalyst(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str
    impactDirection: str # "POSITIVE" or "NEGATIVE"

class RecommendationMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    recommendationVersion: str = "1.0.0"
    thesisVersion: str
    committeeVersion: str
    critiqueVersion: str
    compiledAt: str
    status: RecommendationStatus

class InvestmentRecommendation(BaseModel):
    model_config = ConfigDict(frozen=True)
    recommendationId: str
    thesisId: str
    committeeReviewId: str
    critiqueId: str
    intelligenceId: str
    evidenceId: str
    schemaVersion: str = "1.0.0"
    
    stance: InvestmentStance
    investmentOutlook: str = Field(..., description="Overall outlook: Bullish, Neutral, or Bearish")
    suggestedActions: List[str] = Field(..., description="Context-aware actions. e.g. 'New Investor -> BUY', 'Existing Holder -> HOLD'")
    horizon: TimeHorizon
    conviction: ConvictionLevel
    confidenceScore: float = Field(ge=0.0, le=1.0)
    
    keyPositives: List[str]
    keyRisks: List[str]
    committeeReasons: List[str]
    critiqueHighlights: List[str]
    
    monitoringItems: List[MonitoringItem]
    catalysts: List[RecommendationCatalyst]
    
    meta: RecommendationMetadata
