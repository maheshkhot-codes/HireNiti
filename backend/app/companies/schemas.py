from pydantic import BaseModel


class CompanyCreate(BaseModel):

    name: str

    description: str | None = None

    website: str | None = None

    location: str | None = None