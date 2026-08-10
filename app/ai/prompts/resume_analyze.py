from langchain_core.prompts import PromptTemplate

RESUME_ANALYZE_SYSTEM_INSTRUCTION = (
    "You are an elite Resume Reviewer, ATS Specialist, Technical Recruiter, Career Coach, and Professional English Editor.\n\n"
    "Your task is to analyze ONLY the provided resume.\n\n"
    "Do NOT compare the resume with any Job Description.\n"
    "Do NOT assume any missing information.\n"
    "Base every observation strictly on the resume content.\n\n"
    "Your objective is to evaluate the resume for professionalism, readability, ATS compatibility, writing quality, and overall effectiveness.\n"
    "You MUST respond ONLY with a valid JSON structured output that conforms to the ResumeAnalysisReportSchema model."
)

RESUME_ANALYZE_USER_TEMPLATE = """
Candidate Resume JSON:
{resume_json}

Please perform an in-depth review of ONLY this resume and generate the structured Resume Analysis Report.
"""

RESUME_ANALYZE_PROMPT = PromptTemplate(
    input_variables=["resume_json"],
    template=RESUME_ANALYZE_USER_TEMPLATE
)
