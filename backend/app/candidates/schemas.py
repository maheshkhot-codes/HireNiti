from pydantic import BaseModel


class CandidateProfileCreate(BaseModel):

    phone: str | None = None
    location: str | None = None
    skills: str | None = None
    education: str | None = None
    experience_years: float | None = None
    bio: str | None = None


class CandidateProfileResponse(CandidateProfileCreate):

    id: str
    user_id: str