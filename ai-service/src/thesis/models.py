# ─────────────────────────────────────────────────────────────────
# src/thesis/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable domain schemas for the Investment Thesis Builder.
# Enforces strict type safety and frozen model compliance.
# ─────────────────────────────────────────────────────────────────

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from src.intelligence.models import EvidenceReference

class ThesisStatement(BaseModel):
    """
    A single traceable analysis statement mapping back to an intelligence finding.
    """
    model_config = ConfigDict(frozen=True)
    
    statementId: str
    pillar: str
    finding: str
    ruleId: Optional[str] = None
    decisionTrace: Optional[str] = None
    evidenceReference: Optional[EvidenceReference] = None

class ThesisSection(BaseModel):
    """
    A structured section representing an intelligence pillar within the thesis document.
    """
    model_config = ConfigDict(frozen=True)
    
    title: str
    pillar: str
    statements: List[ThesisStatement]

class ThesisMetadata(BaseModel):
    """
    Provenance logs and compile-time trackers for the thesis.
    """
    model_config = ConfigDict(frozen=True)
    
    schemaVersion: str = "1.0.0"
    compiledAt: str

class InvestmentThesis(BaseModel):
    """
    Root contract linking all sections, scores, and UUIDs to build a complete thesis.
    """
    model_config = ConfigDict(frozen=True)
    
    schemaVersion: str = "1.0.0"
    thesisId: str
    intelligenceId: str
    evidenceId: str
    ticker: str
    overallScore: float
    sections: Dict[str, ThesisSection]
    meta: ThesisMetadata
