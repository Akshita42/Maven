# ─────────────────────────────────────────────────────────────────
# src/core/http_client.py
# ─────────────────────────────────────────────────────────────────
#
# Shared HTTP Client for Python services.
#
# Implements User-Agent headers, timeouts, gzip/deflate decompression,
# and transient failure retries using exponential backoff.
# ─────────────────────────────────────────────────────────────────

import time
import urllib.request
import urllib.error
import gzip
import json
from typing import Any, Optional
from src.utils.logger import logger

class HttpClientError(Exception):
    """Base exception for all HTTP Client operations."""
    pass

class HttpClientTimeoutError(HttpClientError):
    """Raised when an HTTP operation exceeds its timeout threshold."""
    pass

class HttpClientResponseError(HttpClientError):
    """Raised when a server returns a non-2xx status code."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"HTTP error {status_code}: {message}")
        self.status_code = status_code

class HttpClient:
    """
    Lightweight, robust HTTP client wrapping urllib.
    Handles decompression, custom user agents, and exponential backoff retries.
    """
    def __init__(
        self, 
        default_timeout: float = 8.0, 
        max_retries: int = 3, 
        backoff_factor: float = 1.5
    ):
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate'
        }

    def execute(
        self, 
        url: str, 
        method: str = "GET", 
        data: Optional[bytes] = None, 
        headers: Optional[dict] = None, 
        timeout: Optional[float] = None
    ) -> bytes:
        """
        Executes an HTTP request with retry logic.
        Automatically decompresses gzip responses and records performance metrics.
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
            
        req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
        req_timeout = timeout if timeout is not None else self.default_timeout
        
        attempt = 0
        current_delay = 1.0
        start_time = time.perf_counter()
        
        while True:
            attempt += 1
            try:
                logger.info(f"HttpClient: Sending {method} request to {url} (Attempt {attempt}/{self.max_retries})")
                with urllib.request.urlopen(req, timeout=req_timeout) as response:
                    raw_content = response.read()
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    
                    # Log successful request metrics
                    logger.info(f"METRIC: http_request_latency_ms={latency_ms:.2f} url={url} attempts={attempt} status=200")
                    
                    # Decompress gzip/deflate if needed
                    content_encoding = response.info().get('Content-Encoding', '')
                    if 'gzip' in content_encoding:
                        try:
                            content = gzip.decompress(raw_content)
                            logger.info(f"HttpClient: Decompressed gzip payload ({len(content)} bytes).")
                            return content
                        except Exception as e:
                            logger.error(f"HttpClient: Gzip decompression failed: {str(e)}")
                            raise HttpClientError("Failed to decompress server response.")
                    else:
                        # Fallback try-decompression in case headers are missing
                        try:
                            content = gzip.decompress(raw_content)
                            return content
                        except Exception:
                            return raw_content
                            
            except urllib.error.HTTPError as he:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.error(f"HttpClient: Server responded with HTTP status {he.code} on attempt {attempt}")
                logger.info(f"METRIC: http_request_failed url={url} status={he.code} latency_ms={latency_ms:.2f}")
                
                # Check for client errors (e.g. 404, 401, 403) - do not retry these
                if he.code < 500:
                    raise HttpClientResponseError(he.code, he.reason)
                    
                if attempt >= self.max_retries:
                    raise HttpClientResponseError(he.code, he.reason)
                    
            except (urllib.error.URLError, TimeoutError) as ue:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.error(f"HttpClient: Network error or timeout: {str(ue)} on attempt {attempt}")
                logger.info(f"METRIC: http_request_failed url={url} error=network latency_ms={latency_ms:.2f}")
                
                if attempt >= self.max_retries:
                    # Map to timeout or connection exception
                    if "timed out" in str(ue).lower() or isinstance(ue, TimeoutError):
                        raise HttpClientTimeoutError(f"HTTP request timed out: {str(ue)}")
                    raise HttpClientError(f"HTTP connection failed: {str(ue)}")
                    
            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.error(f"HttpClient: Unexpected request exception: {str(e)}")
                logger.info(f"METRIC: http_request_failed url={url} error=unexpected latency_ms={latency_ms:.2f}")
                if attempt >= self.max_retries:
                    raise HttpClientError(f"Unexpected request error: {str(e)}")
            
            # Sleep with exponential backoff before retrying
            logger.warn(f"HttpClient: Retrying request in {current_delay}s...")
            logger.info(f"METRIC: http_retry_count={attempt} url={url}")
            time.sleep(current_delay)
            current_delay *= self.backoff_factor

    def execute_json(
        self, 
        url: str, 
        method: str = "GET", 
        data: Optional[bytes] = None, 
        headers: Optional[dict] = None, 
        timeout: Optional[float] = None
    ) -> Any:
        """Helper executing a request and parsing the output as JSON."""
        response_bytes = self.execute(url, method, data, headers, timeout)
        try:
            return json.loads(response_bytes.decode('utf-8'))
        except json.JSONDecodeError as je:
            logger.error(f"HttpClient: Failed to decode JSON response: {str(je)}")
            raise HttpClientError(f"Malformed JSON response from server: {str(je)}")
