from typing import List


def _list_to_text(title: str, items: List[str]) -> str:
    """
    Convert a list into bullet-point text.

    Example:

    Skills:
    - Python
    - FastAPI
    """

    if not items:
        return ""

    text = f"\n{title}:\n"

    for item in items:
        text += f"- {item}\n"

    return text


def build_resume_document(resume) -> str:
    """
    Convert ResumeSchema into one large text document.
    This text will be sent to Gemini Embedding.
    """

    document = ""

    # ------------------------------------------------
    # Basic Information
    # ------------------------------------------------

    document += f"Name: {resume.name}\n"

    if getattr(resume, "headline", None):
        document += f"Headline: {resume.headline}\n"

    if getattr(resume, "email", None):
        document += f"Email: {resume.email}\n"

    if getattr(resume, "location", None):
        document += f"Location: {resume.location}\n"

    document += "\n"

    # ------------------------------------------------
    # Summary
    # ------------------------------------------------

    if getattr(resume, "summary", None):
        document += "Professional Summary\n"
        document += resume.summary
        document += "\n\n"

    # ------------------------------------------------
    # Skills
    # ------------------------------------------------

    if hasattr(resume, "skills"):

        skills = []

        for skill in resume.skills:

            if isinstance(skill, str):
                skills.append(skill)

            elif hasattr(skill, "name"):
                skills.append(skill.name)

        document += _list_to_text("Technical Skills", skills)

    # ------------------------------------------------
    # Experience
    # ------------------------------------------------

    if hasattr(resume, "experience"):

        document += "\nExperience\n"

        for exp in resume.experience:

            document += (
                f"- {exp.job_title} at {exp.company_name}\n"
            )

            if getattr(exp, "description", None):
                document += exp.description + "\n"

    # ------------------------------------------------
    # Projects
    # ------------------------------------------------

    if hasattr(resume, "projects"):

        document += "\nProjects\n"

        for project in resume.projects:

            document += f"- {project.project_name}\n"

            if getattr(project, "description", None):
                document += project.description + "\n"

            if getattr(project, "technologies", None):

                document += "Technologies: "

                document += ", ".join(project.technologies)

                document += "\n"

    # ------------------------------------------------
    # Education
    # ------------------------------------------------

    if hasattr(resume, "education"):

        document += "\nEducation\n"

        for edu in resume.education:

            document += (
                f"- {edu.degree}"
                f" | {edu.institution}"
            )

            if getattr(edu, "cgpa", None):
                document += f" | CGPA: {edu.cgpa}"

            document += "\n"

    # ------------------------------------------------
    # Certifications
    # ------------------------------------------------

    if hasattr(resume, "certifications"):

        certs = []

        for cert in resume.certifications:

            if isinstance(cert, str):
                certs.append(cert)

            elif hasattr(cert, "name"):
                certs.append(cert.name)

        document += _list_to_text(
            "Certifications",
            certs
        )

    return document.strip()