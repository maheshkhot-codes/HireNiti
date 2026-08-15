from app.database.database import SessionLocal

# Import all models so SQLAlchemy registers
# all tables and foreign keys before queries/commits.
from app.database.models import (
    User,
    CandidateProfile,
    RecruiterProfile,
    Company,
    Job,
    Resume,
    Application,
)

from app.ml.pipeline.job_embedding import (
    save_job_embedding
)


def main():

    db = SessionLocal()

    try:

        jobs = (
            db.query(Job)
            .filter(
                Job.embedding.is_(None)
            )
            .all()
        )

        print(
            f"Jobs without embeddings: {len(jobs)}"
        )

        for job in jobs:

            print(
                f"Generating embedding: {job.title}"
            )

            try:

                save_job_embedding(
                    db=db,
                    job=job
                )

            except Exception as error:

                db.rollback()

                print(
                    f"Failed for '{job.title}': {error}"
                )

        print(
            "Job embedding generation completed."
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()