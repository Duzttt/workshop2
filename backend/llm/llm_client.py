"""
LLM client for calling open-source Llama models via Ollama.

This module provides a small, testable wrapper around the Ollama HTTP API
using an OpenAI-style chat message format:

    messages = [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
    ]
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from urllib import request, error as urlerror

from .settings_llm import get_llm_settings

# Configure logger
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM provider returns an error or cannot be reached."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMConnectionError(LLMError):
    """Raised when LLM provider cannot be reached."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM provider rate limits requests."""
    pass


@dataclass
class LLMResponse:
    """Simple container for LLM responses."""

    content: str
    raw: Dict[str, Any]
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None


class LLMClient:
    """
    Client for interacting with an LLM provider.

    Currently supports:
        - Ollama chat API (non-streaming)
        - Retry logic with exponential backoff
        - Comprehensive error handling
    """

    def __init__(
        self, 
        base_url: Optional[str] = None, 
        model: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        settings = get_llm_settings()
        self.base_url = base_url or settings.base_url
        self.model = model or settings.model
        self.timeout = settings.request_timeout
        self.enabled = settings.enabled
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        
        logger.info(f"Initialized LLM client: model={self.model}, base_url={self.base_url}")

    def _build_ollama_payload(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Build request payload for Ollama /api/chat endpoint."""
        # Ollama expects messages in OpenAI format; we pass through directly.
        return {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(temperature),
                "num_predict": int(max_tokens),
            },
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 200,  # Reduced for shorter, more concise responses
    ) -> LLMResponse:
        """
        Send a chat completion request to the LLM with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (mapped to num_predict)

        Returns:
            LLMResponse with `content` and raw provider response.
        """
        if not self.enabled:
            raise LLMError(
                "LLM is disabled. Set LLM_ENABLED=1 (or remove it) to enable the LLM."
            )

        if not messages:
            raise ValueError("messages must be a non-empty list")

        logger.info(f"Sending chat request to {self.model} with {len(messages)} messages")
        
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                response = self._make_request(messages, temperature, max_tokens)
                response_time = time.time() - start_time
                response.response_time = response_time
                
                logger.info(f"Chat request completed in {response_time:.2f}s, tokens: {response.tokens_used}")
                return response
                
            except urlerror.HTTPError as e:
                last_exception = self._handle_http_error(e, attempt)
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"HTTP error on attempt {attempt + 1}, retrying in {delay}s: {e.code}")
                    time.sleep(delay)
                else:
                    logger.error(f"HTTP error after {self.max_retries + 1} attempts: {e.code}")
                    raise last_exception
                    
            except urlerror.URLError as e:
                last_exception = LLMConnectionError(f"Could not reach LLM provider: {e.reason}")
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"Connection error on attempt {attempt + 1}, retrying in {delay}s: {e.reason}")
                    time.sleep(delay)
                else:
                    logger.error(f"Connection error after {self.max_retries + 1} attempts: {e.reason}")
                    raise last_exception
                    
            except Exception as e:
                last_exception = LLMError(f"Unexpected error while calling LLM: {e}")
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"Unexpected error on attempt {attempt + 1}, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Unexpected error after {self.max_retries + 1} attempts: {e}")
                    raise last_exception
        
        # This should never be reached, but just in case
        raise last_exception or LLMError("Failed to complete LLM request")

    def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float, 
        max_tokens: int
    ) -> LLMResponse:
        """Make the actual HTTP request to the LLM provider."""
        url = f"{self.base_url.rstrip('/')}/api/chat"
        payload = self._build_ollama_payload(messages, temperature, max_tokens)
        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                resp_body = resp.read().decode("utf-8")
        except urlerror.HTTPError as e:
            raise e  # Re-raise to be handled by retry logic
        except urlerror.URLError as e:
            raise e  # Re-raise to be handled by retry logic
        except Exception as e:
            raise LLMError(f"Unexpected error while calling LLM: {e}") from e

        try:
            resp_json = json.loads(resp_body)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON from LLM provider: {e}") from e

        # Ollama chat format: { "message": {"role": "...", "content": "..."}, ... }
        message = resp_json.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise LLMError("LLM returned an empty response")

        return LLMResponse(
            content=content, 
            raw=resp_json, 
            model=self.model,
            tokens_used=resp_json.get("prompt_eval_count", 0) + resp_json.get("eval_count", 0)
        )

    def _handle_http_error(self, error: urlerror.HTTPError, attempt: int) -> LLMError:
        """Handle HTTP errors and determine if they should be retried."""
        # Don't retry certain HTTP status codes
        non_retryable_codes = {400, 401, 403, 404, 422}
        if error.code in non_retryable_codes:
            logger.error(f"Non-retryable HTTP error {error.code}: {error.reason}")
            return LLMError(f"LLM HTTP error {error.code}: {error.reason}")
        
        # Rate limiting - should be retried with longer delays
        if error.code == 429:
            return LLMRateLimitError(f"LLM rate limited: {error.reason}")
        
        # Server errors - should be retried
        if error.code >= 500:
            return LLMError(f"LLM server error {error.code}: {error.reason}")
        
        return LLMError(f"LLM HTTP error {error.code}: {error.reason}")

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay for retries."""
        return self.retry_delay * (self.backoff_factor ** attempt)

    def health_check(self) -> bool:
        """
        Check if the LLM provider is healthy and accessible.
        
        Returns:
            True if the provider is healthy, False otherwise.
        """
        try:
            # Simple health check by listing available models
            url = f"{self.base_url.rstrip('/')}/api/tags"
            req = request.Request(url, method="GET")
            
            with request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    logger.info("LLM provider health check passed")
                    return True
                else:
                    logger.warning(f"LLM provider health check failed with status {resp.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"LLM provider health check failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from the LLM provider.
        
        Returns:
            List of model names.
        """
        try:
            url = f"{self.base_url.rstrip('/')}/api/tags"
            req = request.Request(url, method="GET")
            
            with request.urlopen(req, timeout=10) as resp:
                resp_body = resp.read().decode("utf-8")
                data = json.loads(resp_body)
                
                models = []
                for model in data.get("models", []):
                    models.append(model.get("name", ""))
                
                logger.info(f"Found {len(models)} available models")
                return models
                
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available.
        
        Args:
            model_name: Name of the model to check.
            
        Returns:
            True if the model is available, False otherwise.
        """
        available_models = self.get_available_models()
        return model_name in available_models


_default_client: Optional[LLMClient] = None


def get_llm_client(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> LLMClient:
    """
    Get a process-wide default LLM client instance.

    This avoids re-reading env vars and re-creating clients on each request.
    
    Args:
        max_retries: Maximum number of retry attempts.
        retry_delay: Initial delay between retries in seconds.
        backoff_factor: Multiplier for exponential backoff.
        
    Returns:
        LLMClient instance.
    """
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(
            max_retries=max_retries,
            retry_delay=retry_delay,
            backoff_factor=backoff_factor
        )
    return _default_client


