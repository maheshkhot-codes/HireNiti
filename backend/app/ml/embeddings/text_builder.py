def build_candidate_text(
    skills: str | None,
    education: str | None,
    experience: str | None,
    projects: str | None,
) -> str:

    parts = []

    if skills:
        parts.append(
            f"Skills: {skills}"
        )

    if education:
        parts.append(
            f"Education: {education}"
        )

    if experience:
        parts.append(
            f"Experience: {experience}"
        )

    if projects:
        parts.append(
            f"Projects: {projects}"
        )

    return "\n".join(parts)