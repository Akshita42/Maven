# ─────────────────────────────────────────────────────────────────
# src/thesis/builder.py
# ─────────────────────────────────────────────────────────────────
#
# Stateless Investment Thesis Builder executing pure transformations.
# ─────────────────────────────────────────────────────────────────

import uuid
from datetime import datetime
from typing import Optional

from src.intelligence.models import InvestmentIntelligence, PillarResult
from src.thesis.constants import SECTION_MAP, STATEMENT_PREFIX_MAP
from src.thesis.models import (
    ThesisStatement,
    ThesisSection,
    ThesisMetadata,
    InvestmentThesis
)

class ThesisBuilder:
    """
    Stateless builder that restructures an immutable InvestmentIntelligence
    package into an immutable InvestmentThesis package.
    """
    @staticmethod
    def map_finding_to_rule_id(pillar: str, finding: str) -> Optional[str]:
        """Maps a finding text segment to its matching rule identifier."""
        fl = finding.lower()
        if pillar == "business_quality":
            if "sector" in fl:
                return "BQ-001"
            if "employee" in fl:
                return "BQ-002"
        elif pillar == "financial_health":
            if "operating margin" in fl:
                return "FH-001"
            if "equity" in fl or "roe" in fl:
                return "FH-002"
            if "debt-to-equity" in fl or "solvency" in fl:
                return "FH-003"
            if "current ratio" in fl or "liquidity" in fl:
                return "FH-004"
        elif pillar == "growth":
            if "revenue growth" in fl:
                return "GR-001"
            if "net income growth" in fl:
                return "GR-002"
            if "trend" in fl:
                return "GR-003"
        elif pillar == "valuation":
            if "price" in fl or "trading" in fl:
                return "VL-001"
        elif pillar == "risk":
            if "validation" in fl:
                return "RK-001"
            if "coverage" in fl or "statement fields" in fl:
                return "RK-002"
        elif pillar == "management":
            if "exchange" in fl:
                return "MG-001"
        return None

    @staticmethod
    def build(intelligence: InvestmentIntelligence) -> InvestmentThesis:
        """
        Pure deterministic transformation of InvestmentIntelligence to InvestmentThesis.
        Does not perform calculations, ranking, or LLM-based logic.
        """
        sections = {}
        
        for pillar_key, section_title in SECTION_MAP.items():
            pillar_res: Optional[PillarResult] = intelligence.pillars.get(pillar_key)
            if not pillar_res:
                # If a pillar is missing, initialize an empty section placeholder
                sections[pillar_key] = ThesisSection(
                    title=section_title,
                    pillar=pillar_key,
                    statements=[]
                )
                continue
                
            prefix = STATEMENT_PREFIX_MAP.get(pillar_key, "ST")
            statements = []
            
            # Preserve exact order produced by analyzers
            for idx, finding in enumerate(pillar_res.findings):
                statement_id = f"{prefix}-{idx+1:03d}"
                
                # Trace linkage lookup
                rule_id = ThesisBuilder.map_finding_to_rule_id(pillar_key, finding)
                
                matching_trace = None
                evidence_ref = None
                
                if rule_id:
                    # Lookup matching trace prefix
                    matching_trace = next(
                        (t for t in pillar_res.decisionTraces if t.rule.startswith(rule_id)),
                        None
                    )
                    if matching_trace:
                        evidence_ref = matching_trace.evidenceReference
                
                statements.append(ThesisStatement(
                    statementId=statement_id,
                    pillar=pillar_key,
                    finding=finding,
                    ruleId=rule_id,
                    decisionTrace=matching_trace.rule if matching_trace else "Standard/Warning Lineage Trace",
                    evidenceReference=evidence_ref
                ))
                
            sections[pillar_key] = ThesisSection(
                title=section_title,
                pillar=pillar_key,
                statements=statements
            )
            
        meta = ThesisMetadata(
            schemaVersion="1.0.0",
            compiledAt=datetime.utcnow().isoformat() + "Z"
        )
        
        return InvestmentThesis(
            schemaVersion="1.0.0",
            thesisId=str(uuid.uuid4()),
            intelligenceId=intelligence.intelligenceId,
            evidenceId=intelligence.evidenceId,
            ticker=intelligence.ticker,
            overallScore=intelligence.overallScore,
            sections=sections,
            meta=meta
        )
