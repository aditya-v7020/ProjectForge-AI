"""ProjectForge AI — Regression Tests for LLM Automatic Fallback System."""
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, Field

from backend.app.llm.base import LLMProvider, LLMProviderError, ConfigurationError
from backend.app.llm.fallback import FallbackLLMProvider, mask_sensitive_keys, USER_FRIENDLY_ALL_FAILED_MSG
from backend.app.llm.factory import LLMFactory
from backend.app.core import settings


class SampleSchema(BaseModel):
    name: str = Field(description="Sample name")
    status: str = Field(description="Sample status")


class MockSuccessfulProvider(LLMProvider):
    def __init__(self, name: str, return_text: str = '{"name": "test", "status": "ok"}'):
        super().__init__(api_key=f"sk-test-key-{name}", model_name=f"{name}/model-v1")
        self.provider_name = name
        self.return_text = return_text

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        return self.return_text


class MockFailingProvider(LLMProvider):
    def __init__(self, name: str, error_msg: str = "Rate limit reached 429 quota exceeded"):
        super().__init__(api_key=f"gsk_secret_groq_key_12345", model_name=f"{name}/model-v1")
        self.provider_name = name
        self.error_msg = error_msg

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        raise LLMProviderError(self.error_msg)


def test_groq_success_uses_groq_response():
    groq_prov = MockSuccessfulProvider("groq", '{"name": "groq_res", "status": "ok"}')
    openrouter_prov = MockSuccessfulProvider("openrouter", '{"name": "or_res", "status": "ok"}')

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov])
    result = fallback.generate("hello")

    assert "groq_res" in result


def test_groq_429_falls_back_to_openrouter():
    groq_prov = MockFailingProvider("groq", "Groq API error 429: Rate limit reached 100000 tokens/day limit reached")
    openrouter_prov = MockSuccessfulProvider("openrouter", '{"name": "openrouter_success", "status": "ok"}')

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov])
    result = fallback.generate("hello")

    assert "openrouter_success" in result


def test_groq_and_openrouter_failure_falls_back_to_gemini():
    groq_prov = MockFailingProvider("groq", "Groq API error 429: quota exceeded")
    openrouter_prov = MockFailingProvider("openrouter", "OpenRouter HTTP error 429: rate limit exceeded")
    gemini_prov = MockSuccessfulProvider("gemini", '{"name": "gemini_fallback_success", "status": "ok"}')

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov, gemini_prov])
    result = fallback.generate("hello")

    assert "gemini_fallback_success" in result


def test_all_providers_unavailable_returns_clean_error():
    groq_prov = MockFailingProvider("groq", "Groq 429 limit reached")
    openrouter_prov = MockFailingProvider("openrouter", "OpenRouter 429 limit reached")
    gemini_prov = MockFailingProvider("gemini", "Gemini 429 limit reached")

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov, gemini_prov])

    with pytest.raises(LLMProviderError) as exc_info:
        fallback.generate("hello")

    assert USER_FRIENDLY_ALL_FAILED_MSG in str(exc_info.value)


def test_structured_output_remains_valid_after_fallback():
    groq_prov = MockFailingProvider("groq", "Groq 429 rate limit exceeded")
    openrouter_prov = MockSuccessfulProvider("openrouter", '{"name": "Structured Tech", "status": "verified"}')

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov])
    structured_res = fallback.generate_structured(
        prompt="Generate tech options",
        output_schema=SampleSchema,
    )

    assert isinstance(structured_res, SampleSchema)
    assert structured_res.name == "Structured Tech"
    assert structured_res.status == "verified"


def test_api_keys_never_appear_in_exceptions_or_logs():
    raw_error_text = "API Call failed with gsk_secret12345 and sk-or-secret6789 and AIzaSySecretKey"
    masked = mask_sensitive_keys(raw_error_text)

    assert "gsk_secret12345" not in masked
    assert "sk-or-secret6789" not in masked
    assert "AIzaSySecretKey" not in masked
    assert "<GROQ_API_KEY_MASKED>" in masked
    assert "<OPENROUTER_API_KEY_MASKED>" in masked
    assert "<GEMINI_API_KEY_MASKED>" in masked


def test_all_six_agents_can_use_fallback_mechanism():
    agents = [
        "requirement_analyst",
        "technology_advisor",
        "architecture",
        "task_planner",
        "timeline",
        "critic",
    ]

    with patch.object(settings, "GROQ_API_KEY", "gsk_fake_groq_key"), \
         patch.object(settings, "OPENROUTER_API_KEY", "sk-or-fake_openrouter_key"), \
         patch.object(settings, "GEMINI_API_KEY", "AIzaSyFakeGeminiKey"):

        for agent in agents:
            provider = LLMFactory.get_provider_for_agent(agent)
            assert isinstance(provider, FallbackLLMProvider)
            assert len(provider.providers) >= 2


def test_groq_http_429_fallback_explicit_regression():
    """Explicit regression test: Groq returning HTTP 429 rate limit MUST fall back
    to OpenRouter and produce a valid response — never stuck or raising."""
    groq_prov = MockFailingProvider(
        "groq",
        "Groq API error: status_code=429, "
        "body={'error': {'message': 'Rate limit reached for model llama-3.3-70b-versatile. "
        "100000 tokens per day limit reached. Please try again in 24h.', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"
    )
    openrouter_prov = MockSuccessfulProvider(
        "openrouter",
        '{"name": "OpenRouter Fallback Success", "status": "ok"}'
    )

    fallback = FallbackLLMProvider([groq_prov, openrouter_prov])

    # Test generate
    result = fallback.generate("Analyze project requirements")
    assert "OpenRouter Fallback Success" in result

    # Test generate_structured
    structured = fallback.generate_structured(
        prompt="Generate technology options",
        output_schema=SampleSchema,
    )
    assert isinstance(structured, SampleSchema)
    assert structured.name == "OpenRouter Fallback Success"
    assert structured.status == "ok"


def test_new_format_gemini_key_masked_in_error_output():
    """Regression test: Newer AQ.xxx Gemini keys are masked in error messages."""
    raw_error = "Failed with key AQ.Ab8SomeNewFormatKey1234567890ABCDEF in request"
    masked = mask_sensitive_keys(raw_error)
    assert "AQ.Ab8SomeNewFormatKey1234567890ABCDEF" not in masked
    assert "<GEMINI_API_KEY_MASKED>" in masked
