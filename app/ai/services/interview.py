import anyio
from typing import Optional
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema, InterviewPrepSchema
from app.ai.prompts.interview import INTERVIEW_SYSTEM_INSTRUCTION, INTERVIEW_PROMPT

class InterviewIntelligenceService:
    @staticmethod
    async def prepare_interview(
        resume: ResumeSchema, 
        job_description: Optional[str] = None
    ) -> InterviewPrepSchema:
        """Generate categorized interview preparation questions and guidelines."""
        provider = LLMProviderFactory.get_provider()
        
        resume_json = resume.model_dump_json(indent=2)
        jd_text = job_description if job_description else "No target Job Description was provided. Generate general professional questions tailored to candidate's skills and roles."
        
        prompt = INTERVIEW_PROMPT.format(
            resume_json=resume_json, 
            job_description=jd_text
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            InterviewPrepSchema,
            INTERVIEW_SYSTEM_INSTRUCTION
        )
