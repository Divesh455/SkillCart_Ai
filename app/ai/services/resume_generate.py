import anyio

from app.ai.prompts.resume_generate import (
    RESUME_GENERATE_PROMPT,
    RESUME_GENERATE_SYSTEM_INSTRUCTION,
)
from app.ai.providers.gemini import GeminiProvider
from app.ai.services.models import GenResumeSchema


class ResumeGenerationService:
    @staticmethod
    async def improve_gen_resume(resume: GenResumeSchema) -> GenResumeSchema:
        """Use Gemini to polish and normalize a user-entered generated resume."""
        provider = GeminiProvider()
        prompt = RESUME_GENERATE_PROMPT.format(
            resume_json=resume.model_dump_json(indent=2)
        )

        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            GenResumeSchema,
            RESUME_GENERATE_SYSTEM_INSTRUCTION
        )
