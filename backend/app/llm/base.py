"""ProjectForge AI — LLM Provider Base Class."""
import json
import re
from abc import ABC, abstractmethod
from typing import Optional, Type

from pydantic import BaseModel


class LLMProviderError(Exception):
    """Raised when an LLM provider call fails."""
    pass


class ConfigurationError(Exception):
    """Raised when required configuration (API key) is missing."""
    pass


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: System instructions.
            temperature: Sampling temperature.

        Returns:
            Raw text response from the LLM.

        Raises:
            LLMProviderError: If the API call fails.
        """
        ...

    def generate_structured(
        self,
        prompt: str,
        output_schema: Type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.4,
        max_retries: int = 2,
    ) -> BaseModel:
        """Generate a structured response matching a Pydantic schema.

        Instructs the LLM to output valid JSON, then parses and validates it.

        Args:
            prompt: The user prompt.
            output_schema: Pydantic model class to validate against.
            system_prompt: System instructions.
            temperature: Sampling temperature.
            max_retries: Number of retries on parse failure.

        Returns:
            Validated Pydantic model instance.

        Raises:
            LLMProviderError: If generation or parsing fails after retries.
        """
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        structured_system = (
            f"{system_prompt}\n\n"
            "IMPORTANT: You MUST respond with ONLY a valid JSON object that matches "
            "this exact JSON schema. Do NOT include any text before or after the JSON. "
            "Do NOT wrap it in markdown code blocks.\n\n"
            f"JSON Schema:\n{schema_json}"
        )

        last_error = None
        for attempt in range(max_retries):
            try:
                raw = self.generate(
                    prompt=prompt,
                    system_prompt=structured_system,
                    temperature=max(0.2, temperature - attempt * 0.1),
                )
                parsed = self._parse_json(raw)
                return output_schema.model_validate(parsed)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    prompt = (
                        f"Your previous response was not valid JSON. Error: {e}\n"
                        f"Please respond with ONLY a valid JSON object matching the schema.\n\n"
                        f"Original request:\n{prompt}"
                    )

        raise LLMProviderError(
            f"Failed to get valid structured output after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract and parse JSON from LLM response text."""
        # Try direct parse
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        patterns = [
            r'```json\s*\n?(.*?)\n?\s*```',
            r'```\s*\n?(.*?)\n?\s*```',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Try finding JSON object boundaries
        start = text.find('{')
        if start != -1:
            # Find matching closing brace
            depth = 0
            for i, ch in enumerate(text[start:], start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i + 1])
                        except json.JSONDecodeError:
                            break

        raise ValueError(f"Could not extract valid JSON from response: {text[:500]}...")
