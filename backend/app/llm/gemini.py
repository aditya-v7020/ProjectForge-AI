"""ProjectForge AI — Google Gemini LLM Provider."""
from google import genai
from google.genai import types

from backend.app.llm.base import LLMProvider, LLMProviderError
from backend.app.llm.fallback import mask_sensitive_keys


class GeminiProvider(LLMProvider):
    """Google Gemini API provider using official google-genai SDK."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        super().__init__(api_key, model_name)
        self.client = genai.Client(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Google Gemini."""
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=4096,
            )
            if system_prompt:
                config.system_instruction = system_prompt

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
                raise LLMProviderError("Gemini returned an empty response.")

            return response.text

        except Exception as e:
            masked_msg = mask_sensitive_keys(str(e))
            if "api key" in masked_msg.lower():
                raise LLMProviderError(
                    "Invalid or missing Gemini API key. "
                    "Please check GEMINI_API_KEY in your .env file."
                )
            raise LLMProviderError(f"Gemini API error: {masked_msg}")

