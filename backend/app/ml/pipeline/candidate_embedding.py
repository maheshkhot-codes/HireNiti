from sqlalchemy.orm import Session

from app.resume.models import Resume

from app.ml.embeddings.embedder import (
    generate_embedding
)

from app.ml.embeddings.text_builder import (
    build_candidate_text
)


def create_resume_embedding(
    resume: Resume
) -> list[float]:

    candidate_text = build_candidate_text(
        skills=resume.skills,
        education=resume.education,
        experience=resume.experience,
        projects=resume.projects
    )

    return generate_embedding(
        candidate_text
    )


def save_resume_embedding(
    db: Session,
    resume: Resume
):

    embedding = create_resume_embedding(
        resume
    )

    if not embedding:
        return

    resume.embedding = embedding

    db.commit()

    db.refresh(resume)