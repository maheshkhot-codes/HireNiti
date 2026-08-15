from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session


from app.ml.retrieval.pgvector_candidates import (
    find_similar_candidates_for_job,
)

from app.ml.pipeline.recommendation_scoring import (
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_final_score,
)

from app.ml.ranking.candidate_ranker import (
    rank_candidates,
)

from app.resume.models import Resume

from app.database.models import User

from app.database.session import get_db

from app.auth.dependencies import require_role

from app.applications.models import Application

from app.applications.schemas import (
    ApplicationCreate,
    ApplicationStatusUpdate,
)

from app.jobs.models import Job


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


# =========================================================
# CANDIDATE — APPLY FOR JOB
# =========================================================

@router.post("/")
def apply_for_job(
    application: ApplicationCreate,
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # 1. Check job exists and is active
    # -----------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id,
            Job.status == "active",
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Active job not found",
        )

    # -----------------------------------------------------
    # 2. Check duplicate application
    # -----------------------------------------------------

    existing_application = (
        db.query(Application)
        .filter(
            Application.candidate_id == current_user.id,
            Application.job_id == application.job_id,
        )
        .first()
    )

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You have already applied for this job",
        )

    # -----------------------------------------------------
    # 3. Create application
    # -----------------------------------------------------

    new_application = Application(
        candidate_id=current_user.id,
        job_id=application.job_id,
        status="applied",
    )

    db.add(new_application)

    try:
        db.commit()
        db.refresh(new_application)

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not submit application: {error}",
        )

    return {
        "message": "Application submitted successfully",
        "application_id": str(new_application.id),
        "job_id": str(new_application.job_id),
        "status": new_application.status,
    }


# =========================================================
# CANDIDATE — VIEW MY APPLICATIONS
# =========================================================

@router.get("/my")
def get_my_applications(
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db),
):

    applications = (
        db.query(
            Application,
            Job,
        )
        .join(
            Job,
            Application.job_id == Job.id,
        )
        .filter(
            Application.candidate_id == current_user.id,
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    return [
        {
            "application_id": str(application.id),
            "job_id": str(job.id),
            "job_title": job.title,
            "location": job.location,
            "employment_type": job.employment_type,
            "status": application.status,
            "applied_at": application.applied_at,
        }
        for application, job in applications
    ]


# =========================================================
# RECRUITER — VIEW APPLICATIONS FOR MY JOB
# =========================================================

@router.get("/job/{job_id}")
def get_job_applications(
    job_id: str,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # 1. Verify recruiter owns job
    # -----------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # -----------------------------------------------------
    # 2. Get applications
    # -----------------------------------------------------

    applications = (
        db.query(Application)
        .filter(
            Application.job_id == job_id,
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    return [
        {
            "application_id": str(application.id),
            "candidate_id": str(application.candidate_id),
            "job_id": str(application.job_id),
            "status": application.status,
            "applied_at": application.applied_at,
            "updated_at": application.updated_at,
        }
        for application in applications
    ]


# =========================================================
# RECRUITER — UPDATE APPLICATION STATUS
# =========================================================

@router.patch("/{application_id}/status")
def update_application_status(
    application_id: str,
    status_data: ApplicationStatusUpdate,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # Find application and verify recruiter owns job
    # -----------------------------------------------------

    result = (
        db.query(
            Application,
            Job,
        )
        .join(
            Job,
            Application.job_id == Job.id,
        )
        .filter(
            Application.id == application_id,
            Job.recruiter_id == current_user.id,
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    application, job = result

    # -----------------------------------------------------
    # ApplicationStatusUpdate.status should be an Enum.
    # Use .value when available.
    # -----------------------------------------------------

    status_value = getattr(
        status_data.status,
        "value",
        status_data.status,
    )

    # -----------------------------------------------------
    # Allowed statuses
    # -----------------------------------------------------

    allowed_statuses = {
        "applied",
        "reviewing",
        "shortlisted",
        "interview",
        "rejected",
        "hired",
    }

    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Allowed values: "
                + ", ".join(
                    sorted(allowed_statuses)
                )
            ),
        )

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    application.status = status_value

    try:
        db.commit()
        db.refresh(application)

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not update application status: "
                f"{error}"
            ),
        )

    return {
        "message": "Application status updated",
        "application_id": str(application.id),
        "status": application.status,
    }


# =========================================================
# RECRUITER — AI CANDIDATE RANKING
# =========================================================

@router.get("/job/{job_id}/ai-ranking")
def get_ai_candidate_ranking(
    job_id: str,
    current_user=Depends(
        require_role("recruiter")
    ),
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # 1. Check recruiter owns the job
    # -----------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # -----------------------------------------------------
    # 2. Get applicants
    # -----------------------------------------------------

    applications = (
        db.query(Application)
        .filter(
            Application.job_id == job_id,
        )
        .all()
    )

    if not applications:
        return []

    # -----------------------------------------------------
    # 3. Get candidate resumes by vector similarity
    # -----------------------------------------------------

    similar_candidates = (
        find_similar_candidates_for_job(
            db=db,
            job_id=str(job.id),
            limit=50,
        )
    )

    # -----------------------------------------------------
    # Only candidates who actually applied
    # -----------------------------------------------------

    applicant_ids = {
        str(application.candidate_id)
        for application in applications
    }

    similar_candidates = [
        candidate
        for candidate in similar_candidates
        if str(
            candidate["candidate_id"]
        ) in applicant_ids
    ]

    # -----------------------------------------------------
    # 4. Build ranking features
    # -----------------------------------------------------

    ranked_candidates = []

    for candidate in similar_candidates:

        candidate_id = str(
            candidate["candidate_id"]
        )

        # -------------------------------------------------
        # Get resume
        # -------------------------------------------------

        resume = (
            db.query(Resume)
            .filter(
                Resume.id == candidate["resume_id"]
            )
            .first()
        )

        if not resume:
            continue

        # -------------------------------------------------
        # Semantic score
        # -------------------------------------------------

        semantic_score = float(
            candidate["similarity"]
        )

        # -------------------------------------------------
        # Skill score
        # -------------------------------------------------

        skill_score = calculate_skill_match(
            candidate_skills=resume.skills,
            required_skills=job.required_skills,
        )

        # -------------------------------------------------
        # Experience score
        # -------------------------------------------------

        experience_score = calculate_experience_match(
            candidate_experience=resume.experience,
            experience_min=job.experience_min,
            experience_max=job.experience_max,
        )

        # -------------------------------------------------
        # Education score
        # -------------------------------------------------

        education_score = calculate_education_match(
            candidate_education=resume.education,
            job_education=job.education,
        )

        # -------------------------------------------------
        # Final rule-based score
        # -------------------------------------------------

        final_score = calculate_final_score(
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=experience_score,
            education_score=education_score,
        )

        # -------------------------------------------------
        # Find application
        # -------------------------------------------------

        application = next(
            (
                item
                for item in applications
                if str(
                    item.candidate_id
                ) == candidate_id
            ),
            None,
        )

        # -------------------------------------------------
        # Build candidate object
        # -------------------------------------------------

        ranked_candidates.append(
            {
                "candidate_id": candidate_id,

                "resume_id": str(
                    resume.id
                ),

                "name": None,

                "email": None,

                "application_id": (
                    str(application.id)
                    if application
                    else None
                ),

                "application_status": (
                    application.status
                    if application
                    else None
                ),

                "semantic_score": round(
                    semantic_score,
                    4,
                ),

                "skill_score": round(
                    skill_score,
                    4,
                ),

                "experience_score": round(
                    experience_score,
                    4,
                ),

                "education_score": round(
                    education_score,
                    4,
                ),

                "final_score": round(
                    final_score,
                    4,
                ),
            }
        )

    # -----------------------------------------------------
    # 5. Add candidate name/email
    # -----------------------------------------------------

    for candidate in ranked_candidates:

        user = (
            db.query(User)
            .filter(
                User.id
                == candidate["candidate_id"]
            )
            .first()
        )

        if user:
            candidate["name"] = user.name
            candidate["email"] = user.email

    # -----------------------------------------------------
    # 6. AI ranking
    # -----------------------------------------------------

    ranked_candidates = rank_candidates(
        ranked_candidates
    )

    # -----------------------------------------------------
    # 7. Sort by trained ranking score
    #    Fallback to final_score
    # -----------------------------------------------------

    def ranking_value(candidate):
        ranking_score = candidate.get(
            "ranking_score"
        )

        if ranking_score is not None:
            return float(ranking_score)

        return float(
            candidate.get(
                "final_score",
                0,
            )
        )

    ranked_candidates.sort(
        key=ranking_value,
        reverse=True,
    )

    # -----------------------------------------------------
    # 8. Add rank
    # -----------------------------------------------------

    for index, candidate in enumerate(
        ranked_candidates,
        start=1,
    ):
        candidate["rank"] = index

    return ranked_candidates