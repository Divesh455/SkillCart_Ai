from langchain_core.prompts import PromptTemplate

RESUME_INTEL_SYSTEM_INSTRUCTION = (
    "You are an expert ATS-friendly Resume Parser AI. "
    "Your objective is to read raw text extracted from a resume document and parse it "
    "into a highly structured and normalized JSON format corresponding to the Resume schema.\n"
    "Ensure all dates are normalized (e.g. Month Year or Year). Categorize skills logically "
    "into categories (e.g., Programming Languages, Frameworks, Cloud & DevOps, Databases, Soft Skills). "
    "Normalize skill names (e.g., 'ReactJS' to 'React', 'JS' to 'JavaScript')."
)

RESUME_INTEL_USER_TEMPLATE = """
Here is the raw text extracted from the candidate's resume:
---
{raw_text}
---

Please parse and structure this text. Ensure that Name, Contact, Education, Experience, Projects, Skills, and Certifications are fully extracted. If some details are missing, return empty lists or null values as defined in the schema.
"""

RESUME_INTEL_PROMPT = PromptTemplate(
    input_variables=["raw_text"],
    template=RESUME_INTEL_USER_TEMPLATE
)
