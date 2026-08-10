import anyio
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema, CareerMatchSchema, CareerEnhancementSchema
from app.ai.prompts.career_enhance import CAREER_ENHANCE_SYSTEM_INSTRUCTION, CAREER_ENHANCE_PROMPT

class CareerEnhancementService:
    @staticmethod
    async def enhance_career(
        resume: ResumeSchema, 
        match_report: CareerMatchSchema
    ) -> CareerEnhancementSchema:
        """Generate Resume Flex modifications, cover letter, and personalized learning roadmaps."""
        provider = LLMProviderFactory.get_provider()
        
        resume_json = resume.model_dump_json(indent=2)
        match_json = match_report.model_dump_json(indent=2)
        
        prompt = CAREER_ENHANCE_PROMPT.format(
            resume_json=resume_json, 
            match_report=match_json
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            CareerEnhancementSchema,
            CAREER_ENHANCE_SYSTEM_INSTRUCTION
        )
