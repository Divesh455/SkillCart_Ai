import anyio
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema, ResumeAnalysisReportSchema
from app.ai.prompts.resume_analyze import RESUME_ANALYZE_SYSTEM_INSTRUCTION, RESUME_ANALYZE_PROMPT

class ResumeAnalysisService:
    @staticmethod
    async def analyze_resume(
        resume: ResumeSchema
    ) -> ResumeAnalysisReportSchema:
        """Evaluate resume strictly on its contents for grammar, structure, formatting, ATS, and content quality."""
        provider = LLMProviderFactory.get_provider()
        
        resume_json = resume.model_dump_json(indent=2)
        prompt = RESUME_ANALYZE_PROMPT.format(
            resume_json=resume_json
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            ResumeAnalysisReportSchema,
            RESUME_ANALYZE_SYSTEM_INSTRUCTION
        )
