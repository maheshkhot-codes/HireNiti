from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import User
from app.jobs.models import Job
from app.applications.models import Application


def get_recruiter_dashboard(
    db: Session,
    recruiter_id
):
    # -----------------------------------------------------
    # Total jobs
    # -----------------------------------------------------

    total_jobs = (
        db.query(func.count(Job.id))
        .filter(
            Job.recruiter_id == recruiter_id
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Active jobs
    # -----------------------------------------------------

    active_jobs = (
        db.query(func.count(Job.id))
        .filter(
            Job.recruiter_id == recruiter_id,
            Job.status == "active"
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Total applications
    # -----------------------------------------------------

    total_applications = (
        db.query(func.count(Application.id))
        .join(
            Job,
            Application.job_id == Job.id
        )
        .filter(
            Job.recruiter_id == recruiter_id
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Shortlisted
    # -----------------------------------------------------

    shortlisted = (
        db.query(func.count(Application.id))
        .join(
            Job,
            Application.job_id == Job.id
        )
        .filter(
            Job.recruiter_id == recruiter_id,
            Application.status == "shortlisted"
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Interviews
    # -----------------------------------------------------

    interviews = (
        db.query(func.count(Application.id))
        .join(
            Job,
            Application.job_id == Job.id
        )
        .filter(
            Job.recruiter_id == recruiter_id,
            Application.status == "interview"
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Hired
    # -----------------------------------------------------

    hired = (
        db.query(func.count(Application.id))
        .join(
            Job,
            Application.job_id == Job.id
        )
        .filter(
            Job.recruiter_id == recruiter_id,
            Application.status == "hired"
        )
        .scalar()
        or 0
    )

    return {
        "statistics": {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "shortlisted": shortlisted,
            "interviews": interviews,
            "hired": hired
        }
    }


def get_recruiter_jobs(
    db: Session,
    recruiter_id
):
    jobs = (
        db.query(Job)
        .filter(
            Job.recruiter_id == recruiter_id
        )
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )

    result = []

    for job in jobs:

        applicant_count = (
            db.query(func.count(Application.id))
            .filter(
                Application.job_id == job.id
            )
            .scalar()
            or 0
        )

        shortlisted_count = (
            db.query(func.count(Application.id))
            .filter(
                Application.job_id == job.id,
                Application.status == "shortlisted"
            )
            .scalar()
            or 0
        )

        interview_count = (
            db.query(func.count(Application.id))
            .filter(
                Application.job_id == job.id,
                Application.status == "interview"
            )
            .scalar()
            or 0
        )

        hired_count = (
            db.query(func.count(Application.id))
            .filter(
                Application.job_id == job.id,
                Application.status == "hired"
            )
            .scalar()
            or 0
        )

        result.append(
            {
                "job_id": str(job.id),
                "title": job.title,
                "location": job.location,
                "employment_type": job.employment_type,
                "status": job.status,
                "created_at": job.created_at,
                "applicant_count": applicant_count,
                "shortlisted_count": shortlisted_count,
                "interview_count": interview_count,
                "hired_count": hired_count
            }
        )

    return result