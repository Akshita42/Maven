import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))
from src.infrastructure.llm.gemini_service import GeminiService

gemini = GeminiService()
system_prompt = """You are an expert equity research analyst.
Respond ONLY with a valid JSON object matching this schema:
{
  "business_quality": ["statement 1", "statement 2"],
  "financial_health": ["statement 1", "statement 2"],
  "growth": ["statement 1", "statement 2"],
  "valuation": ["statement 1", "statement 2"],
  "risk": ["statement 1", "statement 2"],
  "management": ["statement 1", "statement 2"],
  "overall": ["overall thesis statement 1", "overall thesis statement 2"]
}"""
user_prompt = "Company Name: Tesla\nSymbol: TSLA\nSector: Auto\nIndustry: Auto\n\nRaw Findings:\n{}"
print("Calling Gemini...")
response = gemini.generate_json_response(system_prompt, user_prompt, max_output_tokens=700)
print("RAW RESPONSE:")
print(repr(response))
print(f"FINISH REASON: {gemini.last_finish_reason}")
