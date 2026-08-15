import numpy as np

from app.ml.ranking.dataset import (
    build_training_dataset,
)

from app.ml.ranking.xgboost_ranker import (
    ranker,
)


def main():

    print("=" * 60)
    print("TalentHive Ranking Model Training")
    print("=" * 60)


    # ========================================================
    # BUILD DATASET
    # ========================================================

    data = build_training_dataset()


    print(
        f"\nTraining records: "
        f"{len(data)}"
    )


    if not data:

        print(
            "No training records found."
        )

        print(
            "Create resumes, jobs and applications first."
        )

        return


    # ========================================================
    # FEATURE MATRIX
    # ========================================================

    X = []

    y = []


    # ========================================================
    # GROUPS
    # ========================================================

    groups = []

    current_candidate = None
    current_group_size = 0


    # ========================================================
    # BUILD FEATURES + LABELS
    # ========================================================

    for row in data:

        X.append(
            [
                float(
                    row["semantic_score"]
                ),

                float(
                    row["skill_score"]
                ),

                float(
                    row["experience_score"]
                ),

                float(
                    row["education_score"]
                ),
            ]
        )


        y.append(
            float(
                row["relevance"]
            )
        )


        candidate_id = (
            row["candidate_id"]
        )


        # ----------------------------------------------------
        # First candidate
        # ----------------------------------------------------

        if current_candidate is None:

            current_candidate = (
                candidate_id
            )

            current_group_size = 1

            continue


        # ----------------------------------------------------
        # Same candidate
        # ----------------------------------------------------

        if candidate_id == current_candidate:

            current_group_size += 1

            continue


        # ----------------------------------------------------
        # Candidate changed
        # ----------------------------------------------------

        groups.append(
            current_group_size
        )


        current_candidate = (
            candidate_id
        )

        current_group_size = 1


    # ========================================================
    # FINAL GROUP
    # ========================================================

    if current_group_size > 0:

        groups.append(
            current_group_size
        )


    # ========================================================
    # NUMPY
    # ========================================================

    X = np.asarray(
        X,
        dtype=np.float32,
    )


    y = np.asarray(
        y,
        dtype=np.float32,
    )


    groups = np.asarray(
        groups,
        dtype=np.int32,
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    print(
        "\nFeature matrix shape:",
        X.shape,
    )


    print(
        "Label shape:",
        y.shape,
    )


    print(
        "Ranking groups:",
        groups.tolist(),
    )


    print(
        "Number of groups:",
        len(groups),
    )


    print(
        "Group size total:",
        int(
            groups.sum()
        ),
    )


    if len(groups) < 2:

        raise ValueError(
            "At least two candidate groups are required "
            "for learning-to-rank training."
        )


    if int(groups.sum()) != len(data):

        raise ValueError(
            "Ranking group sizes do not match "
            "the number of training records."
        )


    # ========================================================
    # LABEL DISTRIBUTION
    # ========================================================

    unique_labels, counts = (
        np.unique(
            y,
            return_counts=True,
        )
    )


    print(
        "\nLabel distribution:"
    )


    for label, count in zip(
        unique_labels,
        counts,
    ):

        print(
            f"  Relevance {int(label)}: "
            f"{int(count)}"
        )


    # ========================================================
    # TRAIN
    # ========================================================

    print(
        "\nStarting XGBoost ranking training..."
    )


    ranker.train(
        X=X,
        y=y,
        group=groups,
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n" + "=" * 60
    )


    print(
        "Ranking model trained successfully."
    )


    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()