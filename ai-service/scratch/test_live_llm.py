import os
import json
from unittest.mock import patch, MagicMock
from src.agent.services.pipeline_service import PipelineService
from src.critique.constants import CritiqueStatus
from src.agent.exceptions import RetryableAgentError, TerminalAgentError
from src.infrastructure.llm.gemini_service import GeminiService
from google.genai.errors import APIError

def print_result(company_name, report):
    print(f"\n==================================================")
    print(f"Result for: {company_name}")
    meta = report.critique.meta
    print(f"Status: {meta.status.value}")
    print(f"Model: {meta.llmModelName}")
    print(f"Tokens: {meta.tokensUsed}")
    print(f"Prompt Version: {meta.promptVersion}")
    print(f"Finish Reason: {meta.finishReason}")
    print(f"Warnings: {meta.compilerReport.validationWarnings}")
    print(f"==================================================")

def test_real_companies():
    companies = ["Apple", "Microsoft", "Nvidia", "Tesla", "UnknownFakeCo123"]
    for c in companies:
        try:
            report = PipelineService.run_from_query(c)
            print_result(c, report)
        except Exception as e:
            print(f"Failed on {c}: {str(e)}")

def test_timeout_fallback():
    print("\n--- Testing Timeout ---")
    with patch.object(GeminiService, '_call_gemini_with_retry', side_effect=RetryableAgentError("Mock Timeout")):
        report = PipelineService.run_from_query("Apple")
        print_result("Apple (Timeout)", report)

def test_network_failure():
    print("\n--- Testing Network Failure ---")
    with patch.object(GeminiService, '_call_gemini_with_retry', side_effect=TerminalAgentError("Mock Network Failure")):
        report = PipelineService.run_from_query("Apple")
        print_result("Apple (Network Failure)", report)

def test_rate_limit():
    print("\n--- Testing Rate Limit (429) ---")
    # Will raise APIError with code 429 inside the real implementation, but here we can just throw RetryableAgentError to test fallback
    with patch.object(GeminiService, '_call_gemini_with_retry', side_effect=RetryableAgentError("Gemini API transient error 429")):
        report = PipelineService.run_from_query("Apple")
        print_result("Apple (Rate Limit)", report)

def test_malformed_json():
    print("\n--- Testing Malformed JSON ---")
    with patch.object(GeminiService, 'generate_json_response', return_value="This is not json {"):
        report = PipelineService.run_from_query("Apple")
        print_result("Apple (Malformed JSON)", report)

def test_hallucinated_ids():
    print("\n--- Testing Hallucinated IDs ---")
    bad_json = """
    {
      "observedAssumptions": [
        {"reviewerId": "BUSINESS", "statementId": "FAKE-ID-999", "description": "Moat holds", "vulnerabilityScore": 0.45, "weaknessRationale": "regulatory shifts"}
      ],
      "observedBiases": [],
      "observedReasoningFlaws": []
    }
    """
    with patch.object(GeminiService, 'generate_json_response', return_value=bad_json):
        report = PipelineService.run_from_query("Apple")
        print_result("Apple (Hallucinated IDs)", report)

if __name__ == "__main__":
    # Ensure api key is set for real tests
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set in env. Setting a dummy key for fallback tests.")
        os.environ["GEMINI_API_KEY"] = "dummy"
        
    test_timeout_fallback()
    test_network_failure()
    test_rate_limit()
    test_malformed_json()
    test_hallucinated_ids()
    
    # Real test
    if os.environ.get("GEMINI_API_KEY") != "dummy":
        test_real_companies()
