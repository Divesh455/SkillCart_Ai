from typing import Any


def _list_to_text(value: Any) -> str:
    if not value:
        return ""

    if isinstance(value, list):
        return "\n".join(
            f"- {item}"
            for item in value
            if item
        )

    return str(value)


def build_job_document(job: dict) -> str:

    parts = []

    if job.get("job_title"):
        parts.append(
            f"Job Title:\n{job['job_title']}"
        )

    if job.get("department"):
        parts.append(
            f"Department:\n{job['department']}"
        )

    if job.get("location"):
        parts.append(
            f"Location:\n{job['location']}"
        )

    experience_min = job.get("experience_min")
    experience_max = job.get("experience_max")

    if experience_min is not None:

        if experience_max is not None:
            experience = (
                f"{experience_min}-{experience_max} years"
            )
        else:
            experience = (
                f"{experience_min}+ years"
            )

        parts.append(
            f"Required Experience:\n{experience}"
        )

    if job.get("project_role"):
        parts.append(
            f"Role:\n{job['project_role']}"
        )

    if job.get("summary"):
        parts.append(
            "Job Summary:\n"
            + job["summary"]
        )

    responsibilities = _list_to_text(
        job.get("responsibilities")
    )

    if responsibilities:
        parts.append(
            "Responsibilities:\n"
            + responsibilities
        )

    required_skills = _list_to_text(
        job.get("required_skills")
    )

    if required_skills:
        parts.append(
            "Required Skills and Requirements:\n"
            + required_skills
        )

    professional_skills = _list_to_text(
        job.get("professional_skills")
    )

    if professional_skills:
        parts.append(
            "Professional Skills:\n"
            + professional_skills
        )

    preferred_skills = _list_to_text(
        job.get("preferred_skills")
    )

    if preferred_skills:
        parts.append(
            "Preferred Skills:\n"
            + preferred_skills
        )

    education = _list_to_text(
        job.get("education")
    )

    if education:
        parts.append(
            "Education Requirements:\n"
            + education
        )

    return "\n\n".join(parts).strip()