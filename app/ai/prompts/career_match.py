from langchain_core.prompts import PromptTemplate

CAREER_MATCH_SYSTEM_INSTRUCTION = (
    "You are a Career Matching Specialist AI. "
    "Your objective is to compare a candidate's structured resume against a target job description. "
    "Calculate an overall matching score and a breakdown for skills, experience, and education alignment. "
    "Perform a detailed skill gap analysis identifying missing skills, their importance for the role, "
    "and estimate the hours of study required for the candidate to acquire each skill."
)

CAREER_MATCH_USER_TEMPLATE = """
Candidate Resume JSON:
{resume_json}

Target Job Description:
{job_description}

Please analyze the match and output a structured Career Match Report.
"""

CAREER_MATCH_PROMPT = PromptTemplate(
    input_variables=["resume_json", "job_description"],
    template=CAREER_MATCH_USER_TEMPLATE
)
