# ─────────────────────────────────────────────────────────────────
# src/critique/ai_engine.py
# ─────────────────────────────────────────────────────────────────
#
# AICritiqueEngine executing LLM evaluations and parsing structured JSON.
# ─────────────────────────────────────────────────────────────────

import json
from typing import Tuple
from src.critique.interfaces import BaseLLMService
from src.critique.models import AICritiqueObservation
from src.thesis.models import InvestmentThesis
from src.committee.models import InvestmentCommitteeReview
from src.infrastructure.llm.prompt_loader import PromptLoader
from src.agent.exceptions import TerminalAgentError

def strip_json_fences(text: str) -> str:
    """
    Cleans leading/trailing backticks and json block indicators from LLM string.
    """
    import re
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

class AICritiqueEngine:
    """
    Interfaces with the BaseLLMService wrapper to qualitatively evaluate
    assumptions, bias categories, and reasoning link leakages.
    """
    @staticmethod
    def evaluate(
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        llm_service: BaseLLMService
    ) -> Tuple[AICritiqueObservation, str, str]:
        import time
        from pydantic import ValidationError
        print("ENTER AICritiqueEngine.evaluate")
        start_t = time.time()
        
        # Build prompt listing the existing assumptions and statements to avoid hallucinations
        assumptions_list = []
        for op in review.opinions:
            for asm in op.assumptions:
                assumptions_list.append(f"- Reviewer: {op.reviewerId}, Assumption: {asm}")
                
        statements_list = []
        for sec_name, sec in thesis.sections.items():
            for stmt in sec.statements:
                statements_list.append(f"- ID: {stmt.statementId}, Section: {sec_name}, Finding: {stmt.finding}")
                
        # Load system prompt dynamically
        system_prompt, prompt_version, prompt_hash = PromptLoader.load_prompt("critique", "1")
        
        user_prompt = (
            f"Here are the assumptions:\n"
            f"{chr(10).join(assumptions_list)}\n\n"
            f"Here are the thesis statements:\n"
            f"{chr(10).join(statements_list)}"
        )
        
        # 1. Call LLM service
        raw_response = llm_service.generate_json_response(system_prompt, user_prompt, timeout=10.0)
        
        print("=== RAW GEMINI RESPONSE (INITIAL) ===")
        print(raw_response)
        print("=====================================")
        
        cleaned_json = strip_json_fences(raw_response)
        
        try:
            print("AICritiqueEngine: attempting JSON parse")
            data = json.loads(cleaned_json)
            obs = AICritiqueObservation(**data)
            print("JSON parsing succeed: YES")
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"JSON parsing or validation failed: {e}")
            print("Implementing retry...")
            # RETRY ONCE
            retry_prompt = user_prompt + "\n\nThe previous response did not satisfy the required JSON schema. Return ONLY valid JSON containing every required field."
            raw_response = llm_service.generate_json_response(system_prompt, retry_prompt, timeout=10.0)
            
            print("=== RAW GEMINI RESPONSE (RETRY) ===")
            print(raw_response)
            print("===================================")
            
            cleaned_json = strip_json_fences(raw_response)
            try:
                data = json.loads(cleaned_json)
                obs = AICritiqueObservation(**data)
            except Exception as retry_e:
                raise RuntimeError(f"LLM validation failed after retry: {str(retry_e)}") from retry_e
            
        elapsed = time.time() - start_t
        print("EXIT AICritiqueEngine.evaluate")
        print(f"Elapsed time: {elapsed:.3f}s")
        print(f"Returned object type: {type(obs).__name__}")
        print("=== VALIDATED JSON (MATCHES Pydantic exactly) ===")
        print(obs.model_dump_json(indent=2))
        print("=================================================")
        return obs, prompt_version, prompt_hash
