from sqlalchemy import text
from sqlalchemy.orm import Session


def find_similar_candidates_for_job(
    db: Session,
    job_id: str,
    limit: int = 50
):
    """
    Find candidates whose resume embeddings are
    most similar to a given job embedding.
    """

    query = text(
        """
        SELECT
            r.id AS resume_id,
            r.candidate_id,

            1 - (
                r.embedding <=> (
                    SELECT embedding
                    FROM jobs
                    WHERE id = :job_id
                )
            ) AS similarity

        FROM resumes r

        WHERE r.embedding IS NOT NULL

          AND r.id IN (
              SELECT DISTINCT ON (candidate_id)
                  id
              FROM resumes
              WHERE embedding IS NOT NULL
              ORDER BY candidate_id, created_at DESC
          )

          AND (
              SELECT embedding
              FROM jobs
              WHERE id = :job_id
          ) IS NOT NULL

        ORDER BY r.embedding <=> (
            SELECT embedding
            FROM jobs
            WHERE id = :job_id
        )

        LIMIT :limit
        """
    )

    result = db.execute(
        query,
        {
            "job_id": job_id,
            "limit": limit
        }
    )

    return result.mappings().all()