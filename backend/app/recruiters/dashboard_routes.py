from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_role

from app.recruiters.dashboard import (
    get_recruiter_dashboard,
    get_recruiter_jobs
)

from app.jobs.models import Job


router = APIRouter(
    prefix="/recruiter/dashboard",
    tags=["Recruiter Dashboard"]
)


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@router.get("/")
def recruiter_dashboard(
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    dashboard = get_recruiter_dashboard(
        db=db,
        recruiter_id=current_user.id
    )

    return dashboard


# =========================================================
# RECRUITER JOBS
# =========================================================

@router.get("/jobs")
def recruiter_dashboard_jobs(
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db)
):

    return get_recruiter_jobs(
        db=db,
        recruiter_id=current_user.id
    )


# =========================================================
# SINGLE JOB OVERVIEW
# =========================================================

@router.get("/jobs/{job_id}")
def recruiter_job_overview(
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

    return {
        "job_id": str(job.id),
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
        "salary_max": job.salary_max,
        "status": job.status
    }