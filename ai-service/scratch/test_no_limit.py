import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

from src.infrastructure.llm.gemini_service import GeminiService

findings_dict = {
  "business_quality": ["The company is great.", "Very strong moat."],
  "financial_health": ["Lots of cash.", "No debt."],
  "growth": ["High growth."],
  "valuation": ["Expensive."],
  "risk": ["High risk."],
  "management": ["Good."]
}

gemini = GeminiService()
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
    "For every section (Business Quality, Financial Health, Growth, Valuation, Risk, Management, Overall), ask yourself and answer through your reasoning:\n"
    "• What do these findings collectively tell us?\n"
    "• Why do they matter to an investor?\n"
    "• What assumptions are being made?\n"
    "• How confident can we be given the available evidence?\n\n"
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

user_prompt = (
    f"Company Name: Tesla\n"
    f"Symbol: TSLA\n"
    f"Sector: Auto\n"
    f"Industry: Auto\n\n"
    f"Raw Findings:\n{json.dumps(findings_dict, separators=(',', ':'))}"
)

print("Calling Gemini without max_output_tokens...")
# We will temporarily mock the config kwargs
from google.genai import types
config = types.GenerateContentConfig(
    system_instruction=system_prompt,
    temperature=gemini.temperature,
    response_mime_type="application/json"
)
response = gemini.client.models.generate_content(
    model=gemini.model_name,
    contents=user_prompt,
    config=config
)
print("RAW RESPONSE Length:", len(response.text))
print("RAW RESPONSE:", repr(response.text))
if response.candidates:
    print(f"FINISH REASON: {response.candidates[0].finish_reason}")
if response.usage_metadata:
    print(f"Completion tokens: {response.usage_metadata.candidates_token_count}")
