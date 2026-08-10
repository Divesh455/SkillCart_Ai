import logging
from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.providers.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import LLMProviderException

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise LLMProviderException("GEMINI_API_KEY is not configured in the environment.")
        self.client = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1
        )

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt))
        try:
            response = self.client.invoke(messages)
            return str(response.content)
        except Exception as e:
            logger.error(f"Gemini generate_text failed: {e}")
            raise LLMProviderException(f"Gemini API error: {str(e)}")

    def generate_structured_output(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_instruction: str = None
    ) -> T:
        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt))
        
        structured_client = self.client.with_structured_output(response_model)
        
        try:
            return structured_client.invoke(messages)
        except Exception as e:
            logger.warning(f"Gemini: First attempt to parse structured output failed: {e}. Retrying once...")
            try:
                # Add validation error notice to retry messages
                retry_messages = messages + [
                    SystemMessage(
                        content=f"Your previous response failed validation: {str(e)}. "
                        "Please correct your formatting to strictly match the schema requirements."
                    )
                ]
                return structured_client.invoke(retry_messages)
            except Exception as retry_err:
                logger.error(f"Gemini: Retry attempt to parse structured output failed: {retry_err}")
                raise LLMProviderException(
                    f"Failed to generate structured output after retry. Original error: {str(e)}. "
                    f"Retry error: {str(retry_err)}"
                )
