from pydantic import BaseModel


class RecruiterProfileCreate(BaseModel):

    company_name: str
    designation: str | None = None
    phone: str | None = None


class RecruiterProfileResponse(RecruiterProfileCreate):

    id: str
    user_id: str