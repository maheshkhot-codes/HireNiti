from sqlalchemy import text
from sqlalchemy.orm import Session


def find_similar_jobs(
    db: Session,
    resume_id: str,
    limit: int = 20
):
    """
    Find the most semantically similar active jobs
    for a candidate resume.

    Uses pgvector cosine distance.
    """

    query = text(
        """
        SELECT
            id,
            title,
            description,
            required_skills,
            preferred_skills,
            education,
            experience_min,
            experience_max,
            location,
            employment_type,
            salary_min,
            salary_max,

            1 - (
                embedding <=> (
                    SELECT embedding
                    FROM resumes
                    WHERE id = :resume_id
                )
            ) AS similarity

        FROM jobs

        WHERE status = 'active'
          AND embedding IS NOT NULL
          AND (
                SELECT embedding
                FROM resumes
                WHERE id = :resume_id
              ) IS NOT NULL

        ORDER BY embedding <=> (
            SELECT embedding
            FROM resumes
            WHERE id = :resume_id
        )

        LIMIT :limit
        """
    )

    result = db.execute(
        query,
        {
            "resume_id": resume_id,
            "limit": limit
        }
    )

    return result.mappings().all()