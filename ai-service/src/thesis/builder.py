# ─────────────────────────────────────────────────────────────────
# src/thesis/builder.py
# ─────────────────────────────────────────────────────────────────
#
# Stateless Investment Thesis Builder executing pure transformations.
# ─────────────────────────────────────────────────────────────────

import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

from src.intelligence.models import InvestmentIntelligence, PillarResult
from src.thesis.constants import SECTION_MAP, STATEMENT_PREFIX_MAP
from src.thesis.models import (
    ThesisStatement,
    ThesisSection,
    ThesisMetadata,
    InvestmentThesis
)
from src.infrastructure.llm.gemini_service import GeminiService
from src.utils.logger import logger

class ThesisBuilder:
    @staticmethod
    def build(intelligence: InvestmentIntelligence) -> InvestmentThesis:
        """
        Uses Gemini to generate a genuine investment thesis based ONLY on the 
        structured findings produced by the deterministic financial analysis.
        """
        # Collect existing deterministic findings
        findings_dict = {}
        for pillar_key, pillar_res in intelligence.pillars.items():
            findings_dict[pillar_key] = pillar_res.findings
            
        system_prompt = (
            "You are an expert equity research analyst. You will be provided with raw, deterministic "
            "financial findings for a company. Your job is to interpret what the findings collectively imply "
            "about the company's investment quality.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. Your job is NOT to summarize the findings.\n"
            "2. Your job is to interpret what the findings collectively imply about the company's investment quality.\n"
            "3. Never repeat the input unless necessary.\n"
            "4. Explain WHY the findings matter.\n"
            "5. Connect related findings together whenever possible.\n"
            "6. Clearly distinguish: Observations (facts from the evidence), Interpretation (what those facts imply), and Conclusion (investment implication).\n"
            "7. If evidence is incomplete or conflicting, explicitly mention the uncertainty instead of assuming.\n"
            "8. Never invent facts, financial metrics, or news.\n"
            "9. Never use external knowledge.\n"
            "10. Base every conclusion only on the provided evidence.\n\n"
            "WRITING STYLE:\n"
"Write like a junior equity research analyst preparing a research note for an investment committee.\n\n"

"Your audience already has access to the financial metrics. Do not simply repeat them. Focus on interpreting what those metrics mean for an investor.\n\n"

"Each statement should explain the relationship between the findings instead of discussing them in isolation.\n\n"

"Prefer reasoning over description.\n\n"

"Instead of listing facts, explain how those facts support or weaken the investment case.\n\n"

"Keep the writing concise, objective and professional.\n\n"

"Avoid exaggerated language, marketing phrases or unnecessary adjectives.\n\n"

"If multiple findings point toward the same conclusion, combine them into one coherent insight rather than producing several repetitive statements.\n\n"

"Every statement should answer the question:\n"

"• What does this mean for an investor?\n\n"
            "For every section (Business Quality, Financial Health, Growth, Valuation, Risk, Management, Overall), ask yourself and answer through your reasoning:\n"
            "• What do these findings collectively tell us?\n"
            "• Why do they matter to an investor?\n"
            "• What assumptions are being made?\n"
            "• How confident can we be given the available evidence?\n\n"
            "Each section should contain one or two high-quality insights.\n"
            "Prefer fewer meaningful observations over many repetitive or overlapping statements.\n\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "business_quality": ["statement 1", "statement 2"],\n'
            '  "financial_health": ["statement 1", "statement 2"],\n'
            '  "growth": ["statement 1", "statement 2"],\n'
            '  "valuation": ["statement 1", "statement 2"],\n'
            '  "risk": ["statement 1", "statement 2"],\n'
            '  "management": ["statement 1", "statement 2"],\n'
            '  "overall": ["overall thesis statement 1", "overall thesis statement 2"]\n'
            "}"
        )
        
        from src.services.company_service import resolve_company_metadata
        company_meta = resolve_company_metadata(intelligence.ticker)
        
        user_prompt = (
            f"Company Name: {company_meta.companyName or intelligence.ticker}\n"
            f"Symbol: {intelligence.ticker}\n"
            f"Sector: {company_meta.sector or 'Unknown'}\n"
            f"Industry: {company_meta.industry or 'Unknown'}\n\n"
            f"Raw Findings:\n{json.dumps(findings_dict, indent=2)}"
        )

        logger.info(f"ThesisBuilder: Calling Gemini for {intelligence.ticker}")
        gemini = GeminiService()
        
        llm_output = None
        for attempt in range(2):
            try:
                response_text = gemini.generate_json_response(system_prompt, user_prompt, timeout=20.0)
                llm_output = GeminiService.parse_json_safely(response_text)
                logger.info(f"ThesisBuilder: JSON extraction succeeded on attempt {attempt+1}. Retry used: {attempt > 0}. Final status: SUCCESS")
                break
            except Exception as e:
                logger.error(f"ThesisBuilder: JSON parse failed on attempt {attempt+1}: {str(e)}")
                if attempt == 1:
                    logger.error("ThesisBuilder: Final parse status: FAILED. Falling back to deterministic findings.")
                    break
        
        if not llm_output:
            llm_output = findings_dict
            llm_output["overall"] = ["Information currently unavailable. Relying on deterministic findings."]
            
        sections = {}
        for pillar_key, section_title in SECTION_MAP.items():
            statements_text = llm_output.get(pillar_key, [])
            prefix = STATEMENT_PREFIX_MAP.get(pillar_key, "ST")
            statements = []
            
            for idx, text in enumerate(statements_text):
                statements.append(ThesisStatement(
                    statementId=f"{prefix}-{idx+1:03d}",
                    pillar=pillar_key,
                    finding=text,
                    ruleId=None,
                    decisionTrace="LLM Synthesized Thesis",
                    evidenceReference=None
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
