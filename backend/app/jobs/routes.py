from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_role

from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobUpdate

from app.ml.pipeline.job_embedding import save_job_embedding

from app.ml.retrieval.pgvector_store import find_similar_jobs

from app.ml.pipeline.recommendation_scoring import (
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_final_score,
)

from app.ml.ranking.ranker import (
    rank_recommendations
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# =========================================================
# CREATE JOB
# =========================================================

@router.post("/")
def create_job(
    job: JobCreate,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    new_job = Job(
        recruiter_id=current_user.id,
        title=job.title,
        description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        education=job.education,
        location=job.location,
        employment_type=job.employment_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        status="draft"
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Generate embedding for the job
    save_job_embedding(
        db=db,
        job=new_job
    )

    return {
        "message": "Job created successfully",
        "job_id": str(new_job.id),
        "status": new_job.status,
        "has_embedding": new_job.embedding is not None
    }


# =========================================================
# GET RECRUITER'S JOBS
# =========================================================

@router.get("/my")
def get_my_jobs(
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(Job)
        .filter(
            Job.recruiter_id == current_user.id
        )
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "required_skills": job.required_skills,
            "location": job.location,
            "employment_type": job.employment_type,
            "status": job.status,
            "created_at": job.created_at
        }
        for job in jobs
    ]


# =========================================================
# PUBLISH JOB
# =========================================================

@router.patch("/{job_id}/publish")
def publish_job(
    job_id: str,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == current_user.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Make sure the job has an embedding
    if job.embedding is None:
        save_job_embedding(
            db=db,
            job=job
        )

    job.status = "active"

    db.commit()
    db.refresh(job)

    return {
        "message": "Job published successfully",
        "job_id": str(job.id),
        "status": job.status,
        "has_embedding": job.embedding is not None
    }


# =========================================================
# UPDATE JOB
# =========================================================

@router.put("/{job_id}")
def update_job(
    job_id: str,
    job_data: JobUpdate,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == current_user.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(job, key, value)

    # Regenerate embedding after job changes
    save_job_embedding(
        db=db,
        job=job
    )

    db.commit()
    db.refresh(job)

    return {
        "message": "Job updated successfully",
        "job_id": str(job.id),
        "has_embedding": job.embedding is not None
    }


# =========================================================
# DELETE JOB
# =========================================================

@router.delete("/{job_id}")
def delete_job(
    job_id: str,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == current_user.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully"
    }


# =========================================================
# GET ACTIVE JOBS
# =========================================================

@router.get("/")
def get_active_jobs(
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(Job)
        .filter(
            Job.status == "active"
        )
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "education": job.education,
            "location": job.location,
            "employment_type": job.employment_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max
        }
        for job in jobs
    ]


# =========================================================
# AI JOB RECOMMENDATIONS
#
# IMPORTANT:
# This route must be before /{job_id}
# =========================================================

@router.get("/recommendations/me")
def get_job_recommendations(
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db)
):

    from app.resume.models import Resume

    # -----------------------------------------------------
    # Get latest resume with embedding
    # -----------------------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.candidate_id == current_user.id,
            Resume.embedding.isnot(None)
        )
        .order_by(
            Resume.created_at.desc()
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Please analyze your resume first"
        )

    # -----------------------------------------------------
    # Retrieve top semantic matches
    # -----------------------------------------------------

    jobs = find_similar_jobs(
        db=db,
        resume_id=str(resume.id),
        limit=20
    )

    recommendations = []

    # -----------------------------------------------------
    # Calculate recruitment scores
    # -----------------------------------------------------

    for job in jobs:

        semantic_score = float(
            job["similarity"]
        )

        # Skill match
        skill_score = calculate_skill_match(
            candidate_skills=resume.skills,
            required_skills=job["required_skills"]
        )

        # Experience match
        experience_score = calculate_experience_match(
            candidate_experience=resume.experience,
            experience_min=job["experience_min"],
            experience_max=job["experience_max"]
        )

        # Education match
        education_score = calculate_education_match(
            candidate_education=resume.education,
            job_education=job["education"]
        )

        # Final rule-based score
        final_score = calculate_final_score(
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=experience_score,
            education_score=education_score
        )

        recommendations.append(
            {
                "job_id": str(job["id"]),

                "title": job["title"],

                "description": job["description"],

                "required_skills": (
                    job["required_skills"]
                ),

                "preferred_skills": (
                    job["preferred_skills"]
                ),

                "education": job["education"],

                "experience_min": (
                    job["experience_min"]
                ),

                "experience_max": (
                    job["experience_max"]
                ),

                "location": job["location"],

                "employment_type": (
                    job["employment_type"]
                ),

                "semantic_score": round(
                    semantic_score,
                    4
                ),

                "skill_score": round(
                    skill_score,
                    4
                ),

                "experience_score": round(
                    experience_score,
                    4
                ),

                "education_score": round(
                    education_score,
                    4
                ),

                "final_score": final_score
            }
        )

    # -----------------------------------------------------
    # XGBoost ranking
    #
    # If the model is not trained yet, rank_recommendations
    # uses final_score as the fallback.
    # -----------------------------------------------------

    recommendations = rank_recommendations(
        recommendations
    )

    # -----------------------------------------------------
    # Return top 10
    # -----------------------------------------------------

    return recommendations[:10]


# =========================================================
# GET SINGLE JOB
#
# Keep this route AFTER /recommendations/me
# =========================================================

@router.get("/{job_id}")
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.status == "active"
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "id": str(job.id),

        "title": job.title,

        "description": job.description,

        "required_skills": job.required_skills,

        "preferred_skills": job.preferred_skills,

        "experience_min": job.experience_min,

        "experience_max": job.experience_max,

        "education": job.education,

        "location": job.location,

        "employment_type": job.employment_type,

        "salary_min": job.salary_min,

        "salary_max": job.salary_max
    }