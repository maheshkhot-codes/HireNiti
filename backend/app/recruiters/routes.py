from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_role

from app.recruiters.models import RecruiterProfile
from app.recruiters.schemas import RecruiterProfileCreate


router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"]
)


@router.post("/profile")
def create_recruiter_profile(
    profile: RecruiterProfileCreate,
    current_user=Depends(require_role("recruiter")),
    db: Session = Depends(get_db)
):

    existing_profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == current_user.id
        )
        .first()
    )

    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Recruiter profile already exists"
        )

    recruiter_profile = RecruiterProfile(
        user_id=current_user.id,
        company_name=profile.company_name,
        designation=profile.designation,
        phone=profile.phone
    )

    db.add(recruiter_profile)
    db.commit()
    db.refresh(recruiter_profile)

    return {
        "message": "Recruiter profile created successfully",
        "profile_id": str(recruiter_profile.id)
    }


@router.get("/profile")
def get_recruiter_profile(
    current_user=Depends(require_role("recruiter")),
    db: Session = Depends(get_db)
):

    profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == current_user.id
        )
        .first()
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found"
        )

    return {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "company_name": profile.company_name,
        "designation": profile.designation,
        "phone": profile.phone
    }