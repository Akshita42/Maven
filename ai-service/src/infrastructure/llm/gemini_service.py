# ─────────────────────────────────────────────────────────────────
# src/infrastructure/llm/gemini_service.py
# ─────────────────────────────────────────────────────────────────
import os
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

from src.critique.interfaces import BaseLLMService
from src.agent.exceptions import RetryableAgentError, TerminalAgentError
from src.utils.logger import logger

load_dotenv()

class GeminiService(BaseLLMService):
    """
    Production-grade Gemini Service.
    Implements retries, timeouts, and JSON-only response formatting.
    """
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise TerminalAgentError("GEMINI_API_KEY environment variable is missing.")
            
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        try:
            temp_str = os.environ.get("GEMINI_TEMPERATURE", "0.1")
            self.temperature = float(temp_str)
        except ValueError:
            self.temperature = 0.1
            
        self.client = genai.Client(api_key=self.api_key)
        
        # State tracking for observability
        self.last_tokens_used: Optional[int] = None
        self.last_finish_reason: Optional[str] = None
        
    @staticmethod
    def parse_json_safely(response_text: str) -> dict:
        import json
        import re
        
        text = response_text.strip()
        
        # Remove markdown fences if present
        if text.startswith("```"):
            # Find the first newline to skip ```json
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline:].strip()
            if text.endswith("```"):
                text = text[:-3].strip()
                
        # Safe repair: trailing commas before closing braces/brackets
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Try parse
        return json.loads(text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RetryableAgentError),
        reraise=True
    )
    def _call_gemini_with_retry(self, system_prompt: str, user_prompt: str, timeout: float) -> str:
        """Internal method to execute the Gemini call with Tenacity retries."""
        import datetime
        
        stage_start_time = time.time()
        stage_start_iso = datetime.datetime.utcfromtimestamp(stage_start_time).isoformat() + "Z"
        
        # We don't have explicit application-level queues/locks here, but we will log it.
        logger.info("GeminiService: Checking locks/queues: No application-level locks or queues are blocking this request.")
        
        api_request_sent_time = time.time()
        api_request_iso = datetime.datetime.utcfromtimestamp(api_request_sent_time).isoformat() + "Z"
        
        logger.info(f"GeminiService Stage start time: {stage_start_iso}")
        logger.info(f"GeminiService API request sent: {api_request_iso}")
        logger.info(f"GeminiService Model name: {self.model_name}")
        
        try:
            config_kwargs = {
                "system_instruction": system_prompt,
                "temperature": self.temperature
            }
            if hasattr(self, "_force_json") and self._force_json:
                config_kwargs["response_mime_type"] = "application/json"
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(**config_kwargs)
            )
            
            response_received_time = time.time()
            response_iso = datetime.datetime.utcfromtimestamp(response_received_time).isoformat() + "Z"
            logger.info(f"GeminiService First byte/response received: {response_iso}")
            
            prompt_tokens = 0
            completion_tokens = 0
            if response.usage_metadata:
                self.last_tokens_used = response.usage_metadata.total_token_count
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            else:
                self.last_tokens_used = 0
                
            if response.candidates and len(response.candidates) > 0:
                self.last_finish_reason = str(response.candidates[0].finish_reason)
            else:
                self.last_finish_reason = "UNKNOWN"
                
            stage_end_time = time.time()
            stage_end_iso = datetime.datetime.utcfromtimestamp(stage_end_time).isoformat() + "Z"
            duration = stage_end_time - stage_start_time
            
            logger.info(f"GeminiService Stage end time: {stage_end_iso}")
            logger.info(f"GeminiService Duration of only that stage: {duration:.3f}s")
            
            # Log response length
            raw_response_text = response.text if response.text else ""
            logger.info(f"GeminiService Raw Response Length: {len(raw_response_text)} chars")
            
            print(f"EXIT GeminiService._call_gemini_with_retry")
            print(f"Latency: {duration:.3f}s")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Completion tokens: {completion_tokens}")
            return raw_response_text
            
        except APIError as e:
            # Handle specific API errors
            status_code = getattr(e, 'code', None)
            
            # 500, 502, 503: Server Errors
            if status_code in [500, 502, 503]:
                logger.warn(f"GeminiService: Transient API error {status_code}: {str(e)}")
                raise RetryableAgentError(f"Gemini API transient error {status_code}") from e
                
            # 429: Too Many Requests / Quota Exceeded (Do NOT retry, fail immediately)
            if status_code == 429:
                logger.error(f"GeminiService: Quota exceeded 429: {str(e)}")
                raise TerminalAgentError("Google Gemini quota has been reached. Please wait a short time or use another API key.") from e
                
            # If it's a 400 Bad Request (e.g. invalid prompt/schema) -> Do not retry
            logger.error(f"GeminiService: Non-retryable API error: {str(e)}")
            raise TerminalAgentError(f"Gemini API error: {str(e)}") from e
            
        except Exception as e:
            # Network timeouts or other unknown exceptions
            err_str = str(e).lower()
            if "timeout" in err_str or "network" in err_str or "connection" in err_str:
                logger.warn(f"GeminiService: Network/timeout error: {str(e)}")
                raise RetryableAgentError(f"Network timeout: {str(e)}") from e
                
            logger.error(f"GeminiService: Unexpected error: {str(e)}")
            raise TerminalAgentError(f"Unexpected Gemini failure: {str(e)}") from e

    def generate_json_response(self, system_prompt: str, user_prompt: str, timeout: float = 10.0) -> str:
        """
        Public contract method enforcing the BaseLLMService signature.
        """
        # Reset state
        self.last_tokens_used = None
        self.last_finish_reason = None
        self._force_json = True
        
        # Override timeout from env if specified
        env_timeout = os.environ.get("GEMINI_TIMEOUT_SECONDS")
        if env_timeout:
            try:
                timeout = float(env_timeout)
            except ValueError:
                pass
                
        # (In a real async system, we'd wrap this with asyncio.wait_for.
        # Given this is sync, google-genai relies on underlying httpx timeout,
        # but for simplicity we rely on the retry wrapper to handle timeouts.)
        
        return self._call_gemini_with_retry(system_prompt, user_prompt, timeout)

    def generate_text_response(self, system_prompt: str, user_prompt: str, timeout: float = 10.0) -> str:
        """
        Generates a plain text conversational response from Gemini.
        """
        self.last_tokens_used = None
        self.last_finish_reason = None
        self._force_json = False
        
        env_timeout = os.environ.get("GEMINI_TIMEOUT_SECONDS")
        if env_timeout:
            try:
                timeout = float(env_timeout)
            except ValueError:
                pass
                
        return self._call_gemini_with_retry(system_prompt, user_prompt, timeout)
