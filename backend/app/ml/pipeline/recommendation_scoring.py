
import re

from app.resume.skill_normalizer import normalize_skills
def normalize(value: str | None) -> str:
    if not value:
        return ""

    return value.lower().strip()




def calculate_skill_match(
    candidate_skills: str | None,
    required_skills: str | None,
) -> float:
    """
    Calculate required-skill coverage using the same
    TalentHive normalization used by resume extraction.

    Example:

        Candidate:
            SpringBoot, REST APIs, Python

        Job:
            Spring Boot, REST API, Python

        Result:
            1.0
    """

    if not candidate_skills or not required_skills:
        return 0.0

    # --------------------------------------------------------
    # Split stored comma/pipe-separated skills
    # --------------------------------------------------------

    candidate_raw = [
        skill.strip()
        for skill in re.split(
            r"[,|]",
            candidate_skills,
        )
        if skill.strip()
    ]

    required_raw = [
        skill.strip()
        for skill in re.split(
            r"[,|]",
            required_skills,
        )
        if skill.strip()
    ]

    if not candidate_raw or not required_raw:
        return 0.0

    # --------------------------------------------------------
    # Normalize both sides using the same TalentHive
    # vocabulary.
    # --------------------------------------------------------

    candidate_normalized = normalize_skills(
        candidate_raw
    )

    required_normalized = normalize_skills(
        required_raw
    )

    # --------------------------------------------------------
    # Use lowercase canonical names for comparison.
    # --------------------------------------------------------

    candidate = {
        skill.strip().lower()
        for skill in candidate_normalized
        if skill.strip()
    }

    required = {
        skill.strip().lower()
        for skill in required_normalized
        if skill.strip()
    }

    if not required:
        return 0.0

    matched = (
        candidate.intersection(
            required
        )
    )

    return round(
        len(matched) / len(required),
        4,
    )
def calculate_experience_match(
    candidate_experience: str | None,
    experience_min,
    experience_max
) -> float:

    if candidate_experience is None:
        return 0.0

    try:
        candidate_years = float(
            candidate_experience
        )
    except (TypeError, ValueError):
        return 0.0

    minimum = (
        float(experience_min)
        if experience_min is not None
        else 0.0
    )

    maximum = (
        float(experience_max)
        if experience_max is not None
        else None
    )

    if candidate_years < minimum:
        return 0.0

    if maximum is not None and candidate_years > maximum:
        return 1.0

    return 1.0


def calculate_education_match(
    candidate_education: str | None,
    job_education: str | None
) -> float:

    if not candidate_education or not job_education:
        return 0.0

    candidate = normalize(candidate_education)
    job = normalize(job_education)

    if candidate in job or job in candidate:
        return 1.0

    candidate_tokens = set(
        re.findall(r"[a-zA-Z]+", candidate)
    )

    job_tokens = set(
        re.findall(r"[a-zA-Z]+", job)
    )

    if not job_tokens:
        return 0.0

    overlap = candidate_tokens.intersection(
        job_tokens
    )

    return len(overlap) / len(job_tokens)


def calculate_final_score(
    semantic_score: float,
    skill_score: float,
    experience_score: float,
    education_score: float
) -> float:

    final_score = (
        0.55 * semantic_score
        + 0.25 * skill_score
        + 0.10 * experience_score
        + 0.10 * education_score
    )

    return round(
        final_score,
        4
    )