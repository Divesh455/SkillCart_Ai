from app.ai.services.models import ResumeSchema


def build_resume_document(resume: ResumeSchema) -> str:
    """
    Convert ResumeSchema into a semantic text document for embeddings.
    """

    parts = []

    # ----------------------------------------------------
    # Basic Information
    # ----------------------------------------------------
    parts.append(f"Candidate Name: {resume.name}")

    if resume.contact:
        parts.append(f"Location: {resume.contact.location}")

    # ----------------------------------------------------
    # Education
    # ----------------------------------------------------
    if resume.education:
        parts.append("\nEducation:")

        for edu in resume.education:
            parts.append(
                f"- {edu.degree} in {edu.major} "
                f"from {edu.institution} "
                f"({edu.start_date} - {edu.end_date}) "
                f"GPA: {edu.gpa}"
            )

    # ----------------------------------------------------
    # Experience
    # ----------------------------------------------------
    if resume.experience:
        parts.append("\nWork Experience:")

        for exp in resume.experience:

            experience = (
                f"- {exp.role} at {exp.company} "
                f"({exp.start_date} - {exp.end_date})"
            )

            parts.append(experience)

            if exp.highlights:
                for item in exp.highlights:
                    parts.append(f"  • {item}")

    # ----------------------------------------------------
    # Projects
    # ----------------------------------------------------
    if resume.projects:
        parts.append("\nProjects:")

        for project in resume.projects:

            project_text = (
                f"- {project.name}: "
                f"{project.description}"
            )

            parts.append(project_text)

            if project.highlights:
                for item in project.highlights:
                    parts.append(f"  • {item}")

    # ----------------------------------------------------
    # Skills
    # ----------------------------------------------------
    if resume.skills:
        parts.append("\nTechnical Skills:")

        for category in resume.skills:

            skill_line = (
                f"{category.category}: "
                + ", ".join(category.skills)
            )

            parts.append(skill_line)

    # ----------------------------------------------------
    # Certifications
    # ----------------------------------------------------
    if resume.certifications:
        parts.append("\nCertifications:")

        for cert in resume.certifications:
            parts.append(
                f"- {cert.name} ({cert.issuer})"
            )

    return "\n".join(parts)