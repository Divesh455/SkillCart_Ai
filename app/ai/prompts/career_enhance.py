from langchain_core.prompts import PromptTemplate

CAREER_ENHANCE_SYSTEM_INSTRUCTION = (
    "You are a Professional Career Coach and Technical Copywriter. "
    "Your objective is to help the candidate enhance their job application by:\n"
    "1. Rewriting and tailoring achievements (Resume Flex) to highlight experiences most relevant to the target job.\n"
    "2. Developing a structured, milestone-based Learning Roadmap to address skill gaps.\n"
    "3. Generating a compelling, professional, customized cover letter that connects their background to the target job."
)

CAREER_ENHANCE_USER_TEMPLATE = """
Candidate Resume JSON:
{resume_json}

Career Match Report (with gaps and priorities):
{match_report}

Please generate the Career Enhancement Package including Resume Flex, rewrite recommendations, learning roadmap, and cover letter.
"""

CAREER_ENHANCE_PROMPT = PromptTemplate(
    input_variables=["resume_json", "match_report"],
    template=CAREER_ENHANCE_USER_TEMPLATE
)
