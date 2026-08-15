from app.ml.ranking.ranker import ranker
from app.ml.ranking.features import (
    build_ranking_features
)


def rank_candidates(
    candidates: list[dict]
) -> list[dict]:

    if not candidates:
        return []

    # -------------------------------------------------
    # XGBoost is not trained yet
    # -------------------------------------------------

    if not ranker.is_trained:

        candidates.sort(
            key=lambda item: item["final_score"],
            reverse=True
        )

        return candidates

    # -------------------------------------------------
    # Build feature matrix
    # -------------------------------------------------

    features = []

    for candidate in candidates:

        features.append(
            build_ranking_features(
                semantic_score=candidate[
                    "semantic_score"
                ],

                skill_score=candidate[
                    "skill_score"
                ],

                experience_score=candidate[
                    "experience_score"
                ],

                education_score=candidate[
                    "education_score"
                ]
            )
        )

    # -------------------------------------------------
    # XGBoost prediction
    # -------------------------------------------------

    scores = ranker.predict(
        features
    )

    # -------------------------------------------------
    # Add ranking score
    # -------------------------------------------------

    for candidate, score in zip(
        candidates,
        scores
    ):

        candidate["ranking_score"] = round(
            float(score),
            4
        )

    # -------------------------------------------------
    # Sort highest first
    # -------------------------------------------------

    candidates.sort(
        key=lambda item: item["ranking_score"],
        reverse=True
    )

    return candidates