def build_job_text(
    title: str,
    description: str,
    required_skills: str | None,
    preferred_skills: str | None,
    education: str | None,
    experience_min,
    experience_max,
) -> str:

    parts = [
        f"Job Title: {title}",
        f"Description: {description}",
    ]

    if required_skills:
        parts.append(
            f"Required Skills: {required_skills}"
        )

    if preferred_skills:
        parts.append(
            f"Preferred Skills: {preferred_skills}"
        )

    if education:
        parts.append(
            f"Education: {education}"
        )

    if experience_min is not None:
        parts.append(
            f"Minimum Experience: {experience_min} years"
        )

    if experience_max is not None:
        parts.append(
            f"Maximum Experience: {experience_max} years"
        )

    return "\n".join(parts)