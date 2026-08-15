def build_ranking_features(
    semantic_score: float,
    skill_score: float,
    experience_score: float,
    education_score: float
) -> list[float]:

    return [
        semantic_score,
        skill_score,
        experience_score,
        education_score
    ]