"""ProjectForge AI — LLM Factory & Tavily Tests."""
import pytest
from backend.app.llm.factory import LLMFactory
from backend.app.llm.base import ConfigurationError
from backend.app.tools.tavily_search import tavily_tool


def test_llm_factory_missing_key():
    """Test LLMFactory raises ConfigurationError when API key is missing."""
    from backend.app.core import settings
    old_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = ""
    try:
        with pytest.raises(ConfigurationError):
            LLMFactory.get_provider("gemini/gemini-2.0-flash")
    finally:
        settings.GEMINI_API_KEY = old_key


def test_tavily_tool_missing_key():
    """Test Tavily tool returns graceful unavailable response when key is missing."""
    # Ensure key is empty for test
    old_key = tavily_tool.api_key
    tavily_tool.api_key = ""

    results = tavily_tool.search("React vs Vue 2025")
    assert results.available is False
    assert "not configured" in results.note

    tavily_tool.api_key = old_key


def test_get_agent_model_returns_model_string_not_api_key():
    """Regression test: Ensure get_agent_model returns provider/model-name and NEVER an API key."""
    from backend.app.core import settings

    old_gemini_key = settings.GEMINI_API_KEY
    old_groq_key = settings.GROQ_API_KEY
    old_or_key = settings.OPENROUTER_API_KEY
    old_tech_model = settings.TECHNOLOGY_AGENT_MODEL

    try:
        # Case 1: Active API key, blank model setting -> returns fallback provider/model-name
        settings.GEMINI_API_KEY = "AIzaSyFakeTestKey12345"
        settings.GROQ_API_KEY = ""
        settings.OPENROUTER_API_KEY = ""
        settings.TECHNOLOGY_AGENT_MODEL = ""
        model_str = settings.get_agent_model("technology_advisor")
        assert "/" in model_str
        assert model_str != settings.GEMINI_API_KEY
        assert model_str.startswith("gemini/")

        # Case 2: Explicitly configured model setting -> returns configured model string
        settings.TECHNOLOGY_AGENT_MODEL = "gemini/gemini-3.6-flash"
        assert settings.get_agent_model("technology_advisor") == "gemini/gemini-3.6-flash"

        # Case 3: Mistakenly configured with an API key -> rejects API key and returns valid provider/model-name fallback
        settings.TECHNOLOGY_AGENT_MODEL = "AIzaSyFakeTestKey12345"
        model_str_fallback = settings.get_agent_model("technology_advisor")
        assert "/" in model_str_fallback
        assert model_str_fallback != "AIzaSyFakeTestKey12345"
        assert model_str_fallback.startswith("gemini/")

    finally:
        settings.GEMINI_API_KEY = old_gemini_key
        settings.GROQ_API_KEY = old_groq_key
        settings.OPENROUTER_API_KEY = old_or_key
        settings.TECHNOLOGY_AGENT_MODEL = old_tech_model


def test_llm_factory_masks_api_key_in_error_message():
    """Ensure LLMFactory never prints or exposes API keys in error output if an invalid key is passed."""
    from backend.app.core import settings
    old_gemini_key = settings.GEMINI_API_KEY
    try:
        settings.GEMINI_API_KEY = "AIzaSyFakeTestKey12345"
        with pytest.raises(ConfigurationError) as exc_info:
            LLMFactory.get_provider("AIzaSyFakeTestKey12345")

        err_msg = str(exc_info.value)
        assert "AIzaSyFakeTestKey12345" not in err_msg
        assert "<API_KEY_MASKED>" in err_msg
    finally:
        settings.GEMINI_API_KEY = old_gemini_key


def test_llm_factory_resolves_all_providers():
    """Test LLMFactory resolves gemini, groq, and openrouter model strings to their respective provider instances."""
    from backend.app.core import settings
    from backend.app.llm.gemini import GeminiProvider
    from backend.app.llm.groq import GroqProvider
    from backend.app.llm.openrouter import OpenRouterProvider

    old_gemini = settings.GEMINI_API_KEY
    old_groq = settings.GROQ_API_KEY
    old_openrouter = settings.OPENROUTER_API_KEY

    try:
        settings.GEMINI_API_KEY = "dummy_gemini_key"
        settings.GROQ_API_KEY = "dummy_groq_key"
        settings.OPENROUTER_API_KEY = "dummy_openrouter_key"

        # Gemini
        p_gemini = LLMFactory.get_provider("gemini/gemini-2.0-flash")
        assert isinstance(p_gemini, GeminiProvider)
        assert p_gemini.model_name == "gemini-2.0-flash"

        # Groq
        p_groq = LLMFactory.get_provider("groq/llama-3.3-70b-versatile")
        assert isinstance(p_groq, GroqProvider)
        assert p_groq.model_name == "llama-3.3-70b-versatile"

        # OpenRouter
        p_or = LLMFactory.get_provider("openrouter/google/gemini-2.0-flash-exp:free")
        assert isinstance(p_or, OpenRouterProvider)
        assert p_or.model_name == "google/gemini-2.0-flash-exp:free"

    finally:
        settings.GEMINI_API_KEY = old_gemini
        settings.GROQ_API_KEY = old_groq
        settings.OPENROUTER_API_KEY = old_openrouter


def test_agent_models_resolve_correct_providers():
    """Test that configuring per-agent models resolves get_provider_for_agent to the requested provider."""
    from backend.app.core import settings
    from backend.app.llm.groq import GroqProvider
    from backend.app.llm.gemini import GeminiProvider

    old_groq = settings.GROQ_API_KEY
    old_gemini = settings.GEMINI_API_KEY
    old_tech_model = settings.TECHNOLOGY_AGENT_MODEL

    try:
        settings.GROQ_API_KEY = "dummy_groq_key"
        settings.GEMINI_API_KEY = "dummy_gemini_key"
        settings.TECHNOLOGY_AGENT_MODEL = "groq/llama-3.3-70b-versatile"

        from backend.app.llm.fallback import FallbackLLMProvider
        p = LLMFactory.get_provider_for_agent("technology_advisor")
        assert isinstance(p, GroqProvider) or (isinstance(p, FallbackLLMProvider) and isinstance(p.providers[0], GroqProvider))
        primary = p.providers[0] if isinstance(p, FallbackLLMProvider) else p
        assert primary.model_name == "llama-3.3-70b-versatile"

    finally:
        settings.GROQ_API_KEY = old_groq
        settings.GEMINI_API_KEY = old_gemini
        settings.TECHNOLOGY_AGENT_MODEL = old_tech_model


def test_new_format_gemini_key_rejected_as_model_string():
    """Regression test: New Gemini API key format (AQ.xxx) is rejected as a model string."""
    from backend.app.core import settings

    old_gemini_key = settings.GEMINI_API_KEY
    old_groq_key = settings.GROQ_API_KEY
    old_tech_model = settings.TECHNOLOGY_AGENT_MODEL

    try:
        settings.GEMINI_API_KEY = "AQ.Ab8FakeNewFormatKey1234567890"
        settings.GROQ_API_KEY = "gsk_fake_groq_fallback_key"
        settings.TECHNOLOGY_AGENT_MODEL = "AQ.Ab8FakeNewFormatKey1234567890"  # Misconfiguration

        # get_agent_model should detect the key and return a valid fallback
        model_str = settings.get_agent_model("technology_advisor")
        assert "/" in model_str, f"Expected provider/model format, got: {model_str}"
        assert model_str != "AQ.Ab8FakeNewFormatKey1234567890"
        assert model_str.startswith("groq/")  # Groq is preferred fallback

        # LLMFactory should reject it with a masked error
        with pytest.raises(ConfigurationError) as exc_info:
            LLMFactory.get_provider("AQ.Ab8FakeNewFormatKey1234567890")
        assert "AQ.Ab8FakeNewFormatKey1234567890" not in str(exc_info.value)
        assert "<API_KEY_MASKED>" in str(exc_info.value)

    finally:
        settings.GEMINI_API_KEY = old_gemini_key
        settings.GROQ_API_KEY = old_groq_key
        settings.TECHNOLOGY_AGENT_MODEL = old_tech_model
