"""ProjectForge AI — Groq LLM Provider."""
from groq import Groq

from backend.app.llm.base import LLMProvider, LLMProviderError
from backend.app.llm.fallback import mask_sensitive_keys


class GroqProvider(LLMProvider):
    """Groq API provider (fast inference for open models)."""

    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key, model_name)
        self.client = Groq(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Groq."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
            )

            if not response.choices:
                raise LLMProviderError("Groq returned no choices.")

            content = response.choices[0].message.content
            if not content:
                raise LLMProviderError("Groq returned an empty response.")

            return content

        except Exception as e:
            masked_msg = mask_sensitive_keys(str(e))
            if "api key" in masked_msg.lower() or "authentication" in masked_msg.lower():
                raise LLMProviderError(
                    "Invalid or missing Groq API key. "
                    "Please check GROQ_API_KEY in your .env file."
                )
            raise LLMProviderError(f"Groq API error: {masked_msg}")
