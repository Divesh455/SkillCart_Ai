from unittest.mock import patch, MagicMock
import pytest
from app.ai.providers.factory import LLMProviderFactory
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.core.exceptions import SkillCartException

def test_factory_returns_gemini_by_default():
    LLMProviderFactory._instance = None  # Reset singleton
    with patch("app.ai.providers.gemini.GeminiProvider.__init__", return_value=None):
        with patch("app.core.config.settings.LLM_PROVIDER", "gemini"):
            with patch("app.core.config.settings.GEMINI_API_KEY", "fake_key"):
                provider = LLMProviderFactory.get_provider()
                assert isinstance(provider, GeminiProvider)

def test_factory_returns_groq():
    LLMProviderFactory._instance = None  # Reset singleton
    with patch("app.ai.providers.groq.GroqProvider.__init__", return_value=None):
        with patch("app.core.config.settings.LLM_PROVIDER", "groq"):
            with patch("app.core.config.settings.GROQ_API_KEY", "fake_key"):
                provider = LLMProviderFactory.get_provider()
                assert isinstance(provider, GroqProvider)

def test_factory_unsupported_provider():
    LLMProviderFactory._instance = None  # Reset singleton
    with patch("app.core.config.settings.LLM_PROVIDER", "unknown_provider"):
        with pytest.raises(SkillCartException) as exc_info:
            LLMProviderFactory.get_provider()
        assert "Unsupported LLM provider configured" in str(exc_info.value)
