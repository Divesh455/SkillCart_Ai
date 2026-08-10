from langchain_core.prompts import PromptTemplate

INTERVIEW_SYSTEM_INSTRUCTION = (
    "You are an expert Technical and Behavioral Interviewer. "
    "Your objective is to generate a comprehensive Interview Preparation Package. "
    "Create realistic questions across categories: Technical, HR, Behavioral (use STAR format in sample answers), "
    "Coding, and Company-Specific (if company details are provided in the JD). "
    "For each question, specify the type, difficulty level, the interviewer's intent, "
    "a high-quality sample answer, and structured evaluation criteria checklist."
)

INTERVIEW_USER_TEMPLATE = """
Candidate Resume JSON:
{resume_json}

Target Job Description (Optional, generate general interview preparation if empty):
{job_description}

Please generate the Interview Preparation Package.
"""

INTERVIEW_PROMPT = PromptTemplate(
    input_variables=["resume_json", "job_description"],
    template=INTERVIEW_USER_TEMPLATE
)
