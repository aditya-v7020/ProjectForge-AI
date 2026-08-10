"""ProjectForge AI — LLM Factory.

Routes model strings like 'gemini/gemini-2.0-flash' to the correct provider
and manages automatic multi-provider fallback.
"""
from typing import List
from backend.app.llm.base import LLMProvider, ConfigurationError
from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.groq import GroqProvider
from backend.app.llm.openrouter import OpenRouterProvider
from backend.app.llm.fallback import FallbackLLMProvider, USER_FRIENDLY_ALL_FAILED_MSG
from backend.app.core import settings


class LLMFactory:
    """Factory that creates LLM providers from model configuration strings.

    Model string format: "provider/model-name"
    Examples:
        - "gemini/gemini-2.0-flash"
        - "groq/llama-3.3-70b-versatile"
        - "openrouter/google/gemini-2.0-flash-exp:free"
    """

    @staticmethod
    def get_provider(model_string: str) -> LLMProvider:
        """Create and return an LLM provider for the given model string.

        Args:
            model_string: Format "provider/model-name".

        Returns:
            Configured LLMProvider instance.

        Raises:
            ConfigurationError: If API key is missing or provider is unknown.
        """
        if not model_string:
            raise ConfigurationError(
                "No LLM model configured. Please set a model in your .env file. "
                "Example: REQUIREMENT_AGENT_MODEL=gemini/gemini-2.0-flash"
            )

        # Mask API key if accidentally passed as model_string
        is_api_key = (
            (settings.GEMINI_API_KEY and model_string == settings.GEMINI_API_KEY) or
            (settings.GROQ_API_KEY and model_string == settings.GROQ_API_KEY) or
            (settings.OPENROUTER_API_KEY and model_string == settings.OPENROUTER_API_KEY) or
            model_string.startswith("AIza") or model_string.startswith("gsk_") or
            model_string.startswith("sk-or-") or model_string.startswith("AQ.")
        )

        parts = model_string.split("/", 1)
        if len(parts) < 2 or is_api_key:
            display_str = "<API_KEY_MASKED>" if is_api_key else model_string
            raise ConfigurationError(
                f"Invalid model string format: '{display_str}'. "
                "Expected format: 'provider/model-name' "
                "(e.g., 'gemini/gemini-2.0-flash')"
            )

        provider_name = parts[0].lower()
        model_name = parts[1]

        if provider_name == "gemini":
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ConfigurationError(
                    "GEMINI_API_KEY not configured. "
                    "Please set it in your .env file to use Gemini models."
                )
            return GeminiProvider(api_key=api_key, model_name=model_name)

        elif provider_name == "groq":
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ConfigurationError(
                    "GROQ_API_KEY not configured. "
                    "Please set it in your .env file to use Groq models."
                )
            return GroqProvider(api_key=api_key, model_name=model_name)

        elif provider_name == "openrouter":
            api_key = settings.OPENROUTER_API_KEY
            if not api_key:
                raise ConfigurationError(
                    "OPENROUTER_API_KEY not configured. "
                    "Please set it in your .env file to use OpenRouter models."
                )
            return OpenRouterProvider(api_key=api_key, model_name=model_name)

        else:
            raise ConfigurationError(
                f"Unknown LLM provider: '{provider_name}'. "
                "Supported providers: gemini, groq, openrouter"
            )

    @staticmethod
    def get_provider_for_agent(agent_name: str) -> LLMProvider:
        """Get the configured LLM provider for a specific agent with automatic fallback.

        Builds candidate list starting with primary configured agent model,
        followed by other configured LLM providers (Groq, OpenRouter, Gemini).

        Args:
            agent_name: One of: requirement_analyst, technology_advisor,
                        architecture, task_planner, timeline, critic

        Returns:
            Configured LLMProvider or FallbackLLMProvider instance.

        Raises:
            ConfigurationError: If no LLM key is configured.
        """
        primary_model_str = settings.get_agent_model(agent_name)
        providers: List[LLMProvider] = []
        seen_provider_names = set()

        # 1. Add primary configured provider
        if primary_model_str:
            try:
                primary_provider = LLMFactory.get_provider(primary_model_str)
                providers.append(primary_provider)
                prov_key = primary_model_str.split('/')[0].lower()
                seen_provider_names.add(prov_key)
            except ConfigurationError:
                pass

        # 2. Add fallback providers based on available API keys
        # Preferred fallback candidates order: Groq, OpenRouter, Gemini
        fallback_candidates = [
            ("groq", settings.GROQ_API_KEY, "groq/llama-3.3-70b-versatile"),
            ("openrouter", settings.OPENROUTER_API_KEY, "openrouter/openrouter/auto"),
            ("gemini", settings.GEMINI_API_KEY, "gemini/gemini-2.0-flash"),
        ]

        for prov_name, api_key, model_str in fallback_candidates:
            if api_key and prov_name not in seen_provider_names:
                try:
                    prov = LLMFactory.get_provider(model_str)
                    providers.append(prov)
                    seen_provider_names.add(prov_name)
                except ConfigurationError:
                    pass

        if not providers:
            raise ConfigurationError(USER_FRIENDLY_ALL_FAILED_MSG)

        if len(providers) == 1:
            return providers[0]

        return FallbackLLMProvider(providers)
