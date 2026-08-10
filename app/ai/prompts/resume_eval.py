from langchain_core.prompts import PromptTemplate

RESUME_EVAL_SYSTEM_INSTRUCTION = (
    "You are an elite Resume Evaluator and Technical Recruiter. "
    "Your task is to analyze a structured resume (JSON) and evaluate it for ATS compliance, "
    "grammar/spelling, formatting, and optionally how well it aligns with a target job description.\n"
    "Identify missing standard keywords, missing standard sections, formatting or layout issues, "
    "and provide highly actionable, context-aware suggestions with concrete rewrite recommendations."
)

RESUME_EVAL_USER_TEMPLATE = """
Candidate Resume JSON:
{resume_json}

Target Job Description (Optional, evaluate generally if empty):
{job_description}

Please perform an in-depth review and output a structured Resume Evaluation Report.
"""

RESUME_EVAL_PROMPT = PromptTemplate(
    input_variables=["resume_json", "job_description"],
    template=RESUME_EVAL_USER_TEMPLATE
)
