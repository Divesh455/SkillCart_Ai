import anyio
import json
from typing import Optional
from app.ai.providers.factory import LLMProviderFactory
from app.ai.services.models import ResumeSchema, InterviewPrepSchema
from app.ai.prompts.interview import INTERVIEW_SYSTEM_INSTRUCTION, INTERVIEW_PROMPT

class InterviewIntelligenceService:
    @staticmethod
    async def prepare_interview(
        resume: ResumeSchema, 
        job_description: Optional[str] = None,
        category: str = "Technical"
    ) -> InterviewPrepSchema:
        """Generate tailored interview preparation questions for a specific category."""
        provider = LLMProviderFactory.get_provider()
        
        # Select only the skills section from the parsed resume data
        skills_data = [skill.model_dump() for skill in resume.skills]
        skills_json = json.dumps(skills_data, indent=2)
        jd_text = job_description if job_description else "No target Job Description was provided."
        
        prompt = (
            f"Candidate Skills JSON:\n{skills_json}\n\n"
            f"Target Job Description:\n{jd_text}\n\n"
            f"Requested Question Category: {category}\n"
            f"Strictly generate ONLY interview questions of the category: '{category}'.\n"
            "Please generate the Interview Preparation Package matching this specific category."
        )
        
        system_instruction = (
            "You are an expert Technical and Behavioral Interviewer. "
            "Your objective is to generate an Interview Preparation Package. "
            f"Create realistic questions strictly for the requested category: '{category}'. "
            "For each question, specify the type (which must match the requested category), difficulty level, the interviewer's intent, "
            "a high-quality sample answer, and structured evaluation criteria checklist."
        )
        
        return await anyio.to_thread.run_sync(
            provider.generate_structured_output,
            prompt,
            InterviewPrepSchema,
            system_instruction
        )

