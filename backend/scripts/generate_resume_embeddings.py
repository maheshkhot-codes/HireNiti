from app.database.database import SessionLocal

# Import all models so SQLAlchemy knows about
# every table and foreign-key relationship.
from app.database.models import (
    User,
    CandidateProfile,
    RecruiterProfile,
    Company,
    Job,
    Resume,
    Application,
)

from app.ml.pipeline.candidate_embedding import (
    save_resume_embedding
)


def main():

    db = SessionLocal()

    try:

        resumes = (
            db.query(Resume)
            .filter(
                Resume.embedding.is_(None)
            )
            .all()
        )

        print(
            f"Resumes without embeddings: {len(resumes)}"
        )

        for resume in resumes:

            print(
                f"Generating embedding: "
                f"{resume.file_name}"
            )

            try:

                save_resume_embedding(
                    db=db,
                    resume=resume
                )

                print(
                    "  ✓ Embedding saved"
                )

            except Exception as error:

                db.rollback()

                print(
                    f"  ✗ Failed: {error}"
                )

        print(
            "\nResume embedding generation completed."
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()