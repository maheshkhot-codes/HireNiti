from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_role

from app.candidates.models import CandidateProfile
from app.candidates.schemas import CandidateProfileCreate


router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)


@router.post("/profile")
def create_candidate_profile(
    profile: CandidateProfileCreate,
    current_user=Depends(require_role("candidate")),
    db: Session = Depends(get_db)
):

    existing_profile = (
        db.query(CandidateProfile)
        .filter(
            CandidateProfile.user_id == current_user.id
        )
        .first()
    )

    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Candidate profile already exists"
        )

    candidate_profile = CandidateProfile(
        user_id=current_user.id,
        phone=profile.phone,
        location=profile.location,
        skills=profile.skills,
        education=profile.education,
        experience_years=profile.experience_years,
        bio=profile.bio
    )

    db.add(candidate_profile)
    db.commit()
    db.refresh(candidate_profile)

    return {
        "message": "Candidate profile created successfully",
        "profile_id": str(candidate_profile.id)
    }


@router.get("/profile")
def get_candidate_profile(
    current_user=Depends(require_role("candidate")),
    db: Session = Depends(get_db)
):

    profile = (
        db.query(CandidateProfile)
        .filter(
            CandidateProfile.user_id == current_user.id
        )
        .first()
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    return {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "phone": profile.phone,
        "location": profile.location,
        "skills": profile.skills,
        "education": profile.education,
        "experience_years": profile.experience_years,
        "bio": profile.bio
    }