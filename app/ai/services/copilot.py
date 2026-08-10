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
    async def generate_guidance(
        resume: ResumeSchema, 
        evaluation: ResumeEvaluationSchema, 
        match: CareerMatchSchema
    ) -> CareerGuidanceReportSchema:
        """Consumes findings from previous engines to build a comprehensive Career Guidance Report."""
        provider = LLMProviderFactory.get_provider()
        
        resume_json = resume.model_dump_json(indent=2)
        evaluation_json = evaluation.model_dump_json(indent=2)
        match_json = match.model_dump_json(indent=2)
        
        prompt = COPILOT_REPORT_PROMPT.format(
            resume_json=resume_json,
            evaluation_json=evaluation_json,
            match_json=match_json
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            CareerGuidanceReportSchema,
            COPILOT_REPORT_SYSTEM_INSTRUCTION
        )

    @staticmethod
    async def chat(
        message: str,
        history: List[ChatMessage],
        resume: Optional[ResumeSchema] = None,
        career_match: Optional[CareerMatchSchema] = None
    ) -> ChatResponseSchema:
        """Engage in interactive career guidance chat using resume context and match history."""
        provider = LLMProviderFactory.get_provider()
        
        # Build context
        context_parts = []
        if resume:
            context_parts.append(f"Candidate Resume Details:\n{resume.model_dump_json(indent=2)}")
        if career_match:
            context_parts.append(f"Candidate Career Matching Details:\n{career_match.model_dump_json(indent=2)}")
            
        context_text = "\n\n".join(context_parts) if context_parts else "No background context provided."
        
        # Format history
        history_lines = []
        for msg in history:
            role_label = "Candidate" if msg.role == "user" else "Copilot"
            history_lines.append(f"{role_label}: {msg.content}")
        history_text = "\n".join(history_lines) if history_lines else "No previous dialogue."
        
        # Construct chat query
        chat_prompt = (
            f"=== Candidate Context ===\n{context_text}\n\n"
            f"=== Conversation History ===\n{history_text}\n\n"
            f"Candidate: {message}\n\n"
            "Copilot response must include the response text and 2-3 suggested follow-up questions."
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            chat_prompt,
            ChatResponseSchema,
            COPILOT_CHAT_SYSTEM_INSTRUCTION
        )
