from sqlalchemy.orm import Session

from app.jobs.models import Job

from app.ml.embeddings.embedder import (
    generate_embedding
)

from app.ml.embeddings.job_text_builder import (
    build_job_text
)


def create_job_embedding(
    job: Job
) -> list[float]:

    job_text = build_job_text(
        title=job.title,
        description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        education=job.education,
        experience_min=job.experience_min,
        experience_max=job.experience_max
    )

    return generate_embedding(
        job_text
    )


def save_job_embedding(
    db: Session,
    job: Job
):

    embedding = create_job_embedding(
        job
    )

    if not embedding:
        return

    job.embedding = embedding

    db.commit()

    db.refresh(job)