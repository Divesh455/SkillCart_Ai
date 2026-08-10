import anyio
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema
from app.ai.prompts.resume_intel import RESUME_INTEL_SYSTEM_INSTRUCTION, RESUME_INTEL_PROMPT

class ResumeIntelligenceService:
    @staticmethod
    async def parse_resume(raw_text: str) -> ResumeSchema:
        """Parse raw text from resume into a structured ResumeSchema."""
        provider = LLMProviderFactory.get_provider()
        prompt = RESUME_INTEL_PROMPT.format(raw_text=raw_text)
        
        # Run sync provider operation in an async worker thread
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            ResumeSchema,
            RESUME_INTEL_SYSTEM_INSTRUCTION
        )
