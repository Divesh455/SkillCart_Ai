import anyio

from app.ai.prompts.resume_generate import (
    RESUME_GENERATE_PROMPT,
    RESUME_GENERATE_SYSTEM_INSTRUCTION,
)
from app.ai.providers.gemini import GeminiProvider
from app.ai.services.models import ResumeSchema


class ResumeGenerationService:
    @staticmethod
    async def improve_resume(resume: ResumeSchema) -> ResumeSchema:
        """Use Gemini to polish and normalize a user-entered resume."""
        provider = GeminiProvider()
        prompt = RESUME_GENERATE_PROMPT.format(
            resume_json=resume.model_dump_json(indent=2)
        )

        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            ResumeSchema,
            RESUME_GENERATE_SYSTEM_INSTRUCTION
        )
