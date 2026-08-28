import anyio
from typing import Optional, List
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import (
    ResumeSchema, 
    ResumeEvaluationSchema, 
    CareerMatchSchema, 
    CareerGuidanceReportSchema, 
    ChatResponseSchema, 
    ChatMessage
)
from app.ai.prompts.copilot import (
    COPILOT_REPORT_SYSTEM_INSTRUCTION, 
    COPILOT_REPORT_PROMPT, 
    COPILOT_CHAT_SYSTEM_INSTRUCTION
)

class CareerCopilotService:
    @staticmethod
    async def chat(
        query: str
    ) -> str:
        """Engage in interactive career guidance chat using the user's query."""
        provider = LLMProviderFactory.get_provider()
        
        return await anyio.to_thread.run_sync(
            provider.generate_text,
            query,
            COPILOT_CHAT_SYSTEM_INSTRUCTION
        )


    @staticmethod
    async def chat(
        query: str
    ) -> str:
        """Engage in interactive career guidance chat using the user's query."""
        provider = LLMProviderFactory.get_provider()
        
        return await anyio.to_thread.run_sync(
            provider.generate_text,
            query,
            COPILOT_CHAT_SYSTEM_INSTRUCTION
        )
