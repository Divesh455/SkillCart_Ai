from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.core.config import settings
from app.core.exceptions import SkillCartException

class LLMProviderFactory:
    _instance: BaseLLMProvider = None

    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        """Returns a singleton LLM provider instance configured via settings."""
        if cls._instance is not None:
            return cls._instance

        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name == "gemini":
            cls._instance = GeminiProvider()
        elif provider_name == "groq":
            cls._instance = GroqProvider()
        else:
            raise SkillCartException(
                f"Unsupported LLM provider configured: '{settings.LLM_PROVIDER}'. "
                "Supported values are 'gemini' or 'groq'."
            )
        return cls._instance
