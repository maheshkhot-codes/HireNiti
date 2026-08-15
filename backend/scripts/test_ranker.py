import numpy as np

from app.ml.ranking.dataset import (
    build_training_dataset,
)

from app.ml.ranking.xgboost_ranker import (
    RecruitmentRanker,
)


def main():

    data = build_training_dataset()

    if not data:
        print("No ranking data found.")
        return

    X = np.asarray(
        [
            [
                float(row["semantic_score"]),
                float(row["skill_score"]),
                float(row["experience_score"]),
                float(row["education_score"]),
            ]
            for row in data
        ],
        dtype=np.float32,
    )

    predictions = (
        RecruitmentRanker().predict(X)
    )

    rows = []

    for row, prediction in zip(
        data,
        predictions,
    ):

        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "job_id": row["job_id"],
                "relevance": row["relevance"],
                "prediction": float(prediction),
            }
        )

    rows.sort(
        key=lambda row: (
            row["candidate_id"],
            -row["prediction"],
        )
    )

    current_candidate = None
    rank = 0

    print("=" * 70)
    print("TalentHive Ranker Test")
    print("=" * 70)

    for row in rows:

        if row["candidate_id"] != current_candidate:

            current_candidate = row["candidate_id"]
            rank = 0

            print(
                f"\nCandidate: {current_candidate}"
            )

        rank += 1

        print(
            f"{rank}. "
            f"Job={row['job_id']} "
            f"Prediction={row['prediction']:.4f} "
            f"Relevance={row['relevance']}"
        )

    print(
        "\n" + "=" * 70
    )
    print("Ranker test complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()