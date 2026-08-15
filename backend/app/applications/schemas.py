from enum import Enum

from pydantic import BaseModel


class ApplicationStatus(str, Enum):

    applied = "applied"

    reviewing = "reviewing"

    shortlisted = "shortlisted"

    interview = "interview"

    rejected = "rejected"

    hired = "hired"


class ApplicationCreate(BaseModel):

    job_id: str


class ApplicationStatusUpdate(BaseModel):

    status: ApplicationStatus