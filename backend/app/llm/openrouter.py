"""ProjectForge AI — OpenRouter LLM Provider."""
import httpx

from backend.app.llm.base import LLMProvider, LLMProviderError
from backend.app.llm.fallback import mask_sensitive_keys


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider (access to many models via one API)."""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model_name: str = "openrouter/auto"):
        super().__init__(api_key, model_name)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate text using OpenRouter."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://projectforge.ai",
                "X-Title": "ProjectForge AI",
            }

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096,
            }

            response = httpx.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()

            data = response.json()

            if "choices" not in data or not data["choices"]:
                raise LLMProviderError("OpenRouter returned no choices.")

            content = data["choices"][0].get("message", {}).get("content", "")
            if not content:
                raise LLMProviderError("OpenRouter returned an empty response.")

            return content

        except httpx.HTTPStatusError as e:
            masked_msg = mask_sensitive_keys(str(e))
            if e.response.status_code == 401:
                raise LLMProviderError(
                    "Invalid or missing OpenRouter API key. "
                    "Please check OPENROUTER_API_KEY in your .env file."
                )
            raise LLMProviderError(f"OpenRouter HTTP error {e.response.status_code}: {masked_msg}")
        except httpx.RequestError as e:
            masked_msg = mask_sensitive_keys(str(e))
            raise LLMProviderError(f"OpenRouter request failed: {masked_msg}")
        except Exception as e:
            masked_msg = mask_sensitive_keys(str(e))
            raise LLMProviderError(f"OpenRouter API error: {masked_msg}")
