from app.ml.ranking.xgboost_ranker import ranker
from app.ml.ranking.features import (
    build_ranking_features
)


def rank_recommendations(
    recommendations: list[dict]
) -> list[dict]:

    if not recommendations:
        return []

    # -------------------------------------------------
    # Fallback when XGBoost is not trained
    # -------------------------------------------------

    if not ranker.is_trained:

        recommendations.sort(
            key=lambda item: item["final_score"],
            reverse=True
        )

        return recommendations


    # -------------------------------------------------
    # Build feature matrix
    # -------------------------------------------------

    features = []

    for item in recommendations:

        features.append(
            build_ranking_features(
                semantic_score=item[
                    "semantic_score"
                ],

                skill_score=item[
                    "skill_score"
                ],

                experience_score=item[
                    "experience_score"
                ],

                education_score=item[
                    "education_score"
                ]
            )
        )


    # -------------------------------------------------
    # Predict ranking score
    # -------------------------------------------------

    scores = ranker.predict(
        features
    )


    # -------------------------------------------------
    # Add ranking score
    # -------------------------------------------------

    for item, score in zip(
        recommendations,
        scores
    ):

        item["ranking_score"] = round(
            float(score),
            4
        )


    # -------------------------------------------------
    # Sort using XGBoost score
    # -------------------------------------------------

    recommendations.sort(
        key=lambda item: item["ranking_score"],
        reverse=True
    )

    return recommendations