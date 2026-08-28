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
        query: str,
        resume_data: Optional[dict] = None
    ) -> str:
        """Engage in interactive career guidance chat using user's query and optional resume context."""
        import json
        provider = LLMProviderFactory.get_provider()
        
        if resume_data:
            # Build context with resume data
            context_text = f"Candidate Resume Details:\n{json.dumps(resume_data, indent=2)}"
            prompt = (
                f"=== Candidate Context ===\n{context_text}\n\n"
                f"=== User Query ===\n{query}\n\n"
                "Please answer the user's query using the candidate resume details provided above if the query is related to the candidate's profile/resume. "
                "Otherwise, answer the query generally and politely."
            )
        else:
            prompt = query
            
        return await anyio.to_thread.run_sync(
            provider.generate_text,
            prompt,
            COPILOT_CHAT_SYSTEM_INSTRUCTION
        )
