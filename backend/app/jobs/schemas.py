from pydantic import BaseModel


class JobCreate(BaseModel):

    title: str

    description: str

    required_skills: str | None = None

    preferred_skills: str | None = None

    experience_min: float | None = None

    experience_max: float | None = None

    education: str | None = None

    location: str | None = None

    employment_type: str | None = None

    salary_min: float | None = None

    salary_max: float | None = None


class JobUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    required_skills: str | None = None

    preferred_skills: str | None = None

    experience_min: float | None = None

    experience_max: float | None = None

    education: str | None = None

    location: str | None = None

    employment_type: str | None = None

    salary_min: float | None = None

    salary_max: float | None = None