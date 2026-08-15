from collections import defaultdict
import random

from sqlalchemy import desc, text

from app.database.database import SessionLocal

from app.applications.models import Application
from app.jobs.models import Job
from app.resume.models import Resume

from app.ml.ranking.labels import get_relevance_label

from app.ml.pipeline.recommendation_scoring import (
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_SEED = 42

NEGATIVE_TO_POSITIVE_RATIO = 5


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def get_semantic_similarity(
    db,
    resume_id: str,
    job_id: str,
) -> float:
    """
    Calculate cosine-style similarity between a candidate
    resume embedding and a job embedding using pgvector.
    """

    query = text(
        """
        SELECT
            1 - (
                r.embedding <=> j.embedding
            ) AS similarity
        FROM resumes r
        CROSS JOIN jobs j
        WHERE r.id = :resume_id
          AND j.id = :job_id
          AND r.embedding IS NOT NULL
          AND j.embedding IS NOT NULL
        """
    )

    result = db.execute(
        query,
        {
            "resume_id": resume_id,
            "job_id": job_id,
        },
    ).scalar()

    if result is None:
        return 0.0

    return float(result)


# ============================================================
# BUILD RANKING DATASET
# ============================================================

def build_training_dataset():
    """
    Build candidate-job pairs for learning-to-rank.

    Rules:

    1. Use only the latest embedded resume for each candidate.
    2. Use all jobs that have embeddings.
    3. Existing applications use their real relevance label.
    4. Non-applied candidate/job pairs are negative examples.
    5. Negative examples are down-sampled to reduce imbalance.
    6. Return exactly one row for each candidate/job pair.
    """

    db = SessionLocal()

    try:

        # ====================================================
        # 1. LOAD ALL EMBEDDED RESUMES
        # ====================================================

        resume_rows = (
            db.query(
                Resume
            )
            .filter(
                Resume.embedding.isnot(None)
            )
            .order_by(
                Resume.candidate_id,
                desc(
                    Resume.created_at
                ),
            )
            .all()
        )

        if not resume_rows:
            return []


        # ====================================================
        # 2. KEEP ONLY LATEST RESUME PER CANDIDATE
        # ====================================================

        candidate_resumes = {}

        for resume in resume_rows:

            candidate_id = str(
                resume.candidate_id
            )

            if candidate_id not in candidate_resumes:

                candidate_resumes[
                    candidate_id
                ] = resume


        resumes = list(
            candidate_resumes.values()
        )


        # ====================================================
        # 3. LOAD JOBS WITH EMBEDDINGS
        # ====================================================

        jobs = (
            db.query(
                Job
            )
            .filter(
                Job.embedding.isnot(None)
            )
            .all()
        )

        if not jobs:
            return []


        # ====================================================
        # 4. LOAD APPLICATIONS
        # ====================================================

        applications = (
            db.query(
                Application
            )
            .all()
        )


        # ====================================================
        # 5. APPLICATION LOOKUP
        # ====================================================

        application_lookup = {}

        for application in applications:

            key = (
                str(
                    application.candidate_id
                ),
                str(
                    application.job_id
                ),
            )

            # If duplicates exist in the database,
            # keep the latest application encountered.
            application_lookup[
                key
            ] = application


        # ====================================================
        # 6. BUILD ALL CANDIDATE/JOB PAIRS
        # ====================================================

        rows = []

        for resume in resumes:

            candidate_id = str(
                resume.candidate_id
            )


            for job in jobs:

                job_id = str(
                    job.id
                )


                pair_key = (
                    candidate_id,
                    job_id,
                )


                # ------------------------------------------------
                # Existing application?
                # ------------------------------------------------

                application = (
                    application_lookup.get(
                        pair_key
                    )
                )


                # ------------------------------------------------
                # Relevance
                # ------------------------------------------------

                if application is not None:

                    relevance = (
                        get_relevance_label(
                            application.status
                        )
                    )

                else:

                    # No application = negative example.
                    relevance = 0


                # =================================================
                # SEMANTIC SCORE
                # =================================================

                semantic_score = (
                    get_semantic_similarity(
                        db=db,
                        resume_id=str(
                            resume.id
                        ),
                        job_id=job_id,
                    )
                )


                # =================================================
                # SKILL SCORE
                # =================================================

                skill_score = (
                    calculate_skill_match(
                        candidate_skills=
                            resume.skills,

                        required_skills=
                            job.required_skills,
                    )
                )


                # =================================================
                # EXPERIENCE SCORE
                # =================================================

                experience_score = (
                    calculate_experience_match(
                        candidate_experience=
                            resume.experience,

                        experience_min=
                            job.experience_min,

                        experience_max=
                            job.experience_max,
                    )
                )


                # =================================================
                # EDUCATION SCORE
                # =================================================

                education_score = (
                    calculate_education_match(
                        candidate_education=
                            resume.education,

                        job_education=
                            job.education,
                    )
                )


                # =================================================
                # STORE ROW
                # =================================================

                rows.append(
                    {
                        "candidate_id":
                            candidate_id,

                        "job_id":
                            job_id,

                        "semantic_score":
                            float(
                                semantic_score
                            ),

                        "skill_score":
                            float(
                                skill_score
                            ),

                        "experience_score":
                            float(
                                experience_score
                            ),

                        "education_score":
                            float(
                                education_score
                            ),

                        "relevance":
                            int(
                                relevance
                            ),
                    }
                )


        # ====================================================
        # 7. GROUP BY CANDIDATE
        # ====================================================

        grouped_rows = defaultdict(list)

        for row in rows:

            grouped_rows[
                row["candidate_id"]
            ].append(
                row
            )


        # ====================================================
        # 8. BALANCED NEGATIVE SAMPLING
        # ====================================================

        random.seed(
            RANDOM_SEED
        )

        balanced_rows = []


        for candidate_id in sorted(
            grouped_rows.keys()
        ):

            candidate_rows = (
                grouped_rows[
                    candidate_id
                ]
            )


            positive_rows = [
                row

                for row in candidate_rows

                if row["relevance"] > 0
            ]


            negative_rows = [
                row

                for row in candidate_rows

                if row["relevance"] == 0
            ]


            # ----------------------------------------------------
            # Candidate has positive examples.
            # ----------------------------------------------------

            if positive_rows:

                max_negatives = (
                    len(
                        positive_rows
                    )
                    *
                    NEGATIVE_TO_POSITIVE_RATIO
                )


                if len(
                    negative_rows
                ) > max_negatives:

                    negative_rows = random.sample(
                        negative_rows,
                        max_negatives,
                    )


                balanced_rows.extend(
                    positive_rows
                )

                balanced_rows.extend(
                    negative_rows
                )


            # ----------------------------------------------------
            # Candidate has no positive examples.
            # ----------------------------------------------------

            else:

                balanced_rows.extend(
                    negative_rows[:5]
                )


        # ====================================================
        # 9. FINAL SORT
        # ====================================================

        balanced_rows.sort(
            key=lambda row: (
                row["candidate_id"],
                row["job_id"],
            )
        )


        # ====================================================
        # 10. SAFETY CHECK
        # ====================================================

        unique_pairs = {
            (
                row["candidate_id"],
                row["job_id"],
            )
            for row in balanced_rows
        }


        if len(unique_pairs) != len(
            balanced_rows
        ):

            raise RuntimeError(
                "Duplicate candidate/job pairs "
                "were found in the ranking dataset."
            )


        return balanced_rows


    finally:

        db.close()