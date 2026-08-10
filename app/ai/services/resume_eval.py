import anyio
from typing import Optional
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema, ResumeEvaluationSchema
from app.ai.prompts.resume_eval import RESUME_EVAL_SYSTEM_INSTRUCTION, RESUME_EVAL_PROMPT

class ResumeEvaluationService:
    @staticmethod
    async def evaluate_resume(
        resume: ResumeSchema, 
        job_description: Optional[str] = None
    ) -> ResumeEvaluationSchema:
        """Evaluate resume against ATS compliance rules and optional job description alignment."""
        provider = LLMProviderFactory.get_provider()
        
        resume_json = resume.model_dump_json(indent=2)
        prompt = RESUME_EVAL_PROMPT.format(
            resume_json=resume_json, 
            job_description=job_description
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            ResumeEvaluationSchema,
            RESUME_EVAL_SYSTEM_INSTRUCTION
        )

