"""ProjectForge AI — Fallback LLM Provider Wrapper.

Provides automatic provider failover when rate limits (HTTP 429), quota limits,
or provider errors occur.
"""
import logging
import re
import time
from typing import List, Type
from pydantic import BaseModel

from backend.app.llm.base import LLMProvider, LLMProviderError, ConfigurationError

logger = logging.getLogger(__name__)

USER_FRIENDLY_ALL_FAILED_MSG = (
    "AI provider temporarily unavailable. All configured providers have "
    "reached their limits or are unavailable. Please try again later."
)


def mask_sensitive_keys(text: str) -> str:
    """Mask any API keys in error strings, exception text, or logs."""
    if not text:
        return ""
    text = re.sub(r'gsk_[A-Za-z0-9_-]+', '<GROQ_API_KEY_MASKED>', text)
    text = re.sub(r'sk-or-[A-Za-z0-9_-]+', '<OPENROUTER_API_KEY_MASKED>', text)
    # Classic AIzaSy... format
    text = re.sub(r'AIzaSy[A-Za-z0-9_-]+', '<GEMINI_API_KEY_MASKED>', text)
    # Newer AQ.Ab8... format (Google Cloud API keys)
    text = re.sub(r'AQ\.[A-Za-z0-9_-]{20,}', '<GEMINI_API_KEY_MASKED>', text)
    return text


def is_transient_error(e: Exception) -> bool:
    """Check if an exception is likely a transient rate-limit or network timeout error."""
    msg = str(e).lower()
    transient_indicators = [
        "429", "rate_limit", "resource_exhausted", "quota", "timeout",
        "502", "503", "504", "connection", "overloaded"
    ]
    return any(ind in msg for ind in transient_indicators)


class FallbackLLMProvider(LLMProvider):
    """LLM Provider wrapper that automatically falls back across candidate providers

    when rate limits (429), quota limits, or network errors occur.
    """

    def __init__(self, providers: List[LLMProvider]):
        if not providers:
            raise ConfigurationError(USER_FRIENDLY_ALL_FAILED_MSG)

        primary = providers[0]
        super().__init__(api_key=primary.api_key, model_name=primary.model_name)
        self.providers = providers

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate text with automatic fallback across providers."""
        last_error = None

        for idx, provider in enumerate(self.providers):
            for attempt in range(2):
                try:
                    logger.info(
                        f"FallbackLLMProvider: Executing generate with candidate {idx + 1}/{len(self.providers)}: {provider.model_name} (Attempt {attempt + 1})"
                    )
                    return provider.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                    )
                except Exception as e:
                    last_error = e
                    masked_err = mask_sensitive_keys(str(e))
                    if attempt < 1 and is_transient_error(e):
                        backoff = (attempt + 1) * 1.5
                        logger.warning(
                            f"FallbackLLMProvider: Candidate {provider.model_name} hit transient error: {masked_err}. Retrying in {backoff}s..."
                        )
                        time.sleep(backoff)
                    else:
                        logger.warning(
                            f"FallbackLLMProvider: Provider candidate {idx + 1} ({provider.model_name}) failed: {masked_err}. "
                            "Attempting fallback to next configured provider..."
                        )
                        break

        raise LLMProviderError(USER_FRIENDLY_ALL_FAILED_MSG)

    def generate_structured(
        self,
        prompt: str,
        output_schema: Type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.4,
        max_retries: int = 2,
    ) -> BaseModel:
        """Generate structured output with automatic fallback across providers."""
        last_error = None

        for idx, provider in enumerate(self.providers):
            for attempt in range(2):
                try:
                    logger.info(
                        f"FallbackLLMProvider: Executing generate_structured with candidate {idx + 1}/{len(self.providers)}: {provider.model_name} (Attempt {attempt + 1})"
                    )
                    return provider.generate_structured(
                        prompt=prompt,
                        output_schema=output_schema,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_retries=max_retries,
                    )
                except Exception as e:
                    last_error = e
                    masked_err = mask_sensitive_keys(str(e))
                    if attempt < 1 and is_transient_error(e):
                        backoff = (attempt + 1) * 1.5
                        logger.warning(
                            f"FallbackLLMProvider: Candidate {provider.model_name} hit transient structured error: {masked_err}. Retrying in {backoff}s..."
                        )
                        time.sleep(backoff)
                    else:
                        logger.warning(
                            f"FallbackLLMProvider: Provider candidate {idx + 1} ({provider.model_name}) failed structured output: {masked_err}. "
                            "Attempting fallback to next configured provider..."
                        )
                        break

        raise LLMProviderError(USER_FRIENDLY_ALL_FAILED_MSG)

