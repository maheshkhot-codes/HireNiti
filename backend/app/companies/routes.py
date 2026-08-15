from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_role

from app.companies.models import Company
from app.companies.schemas import CompanyCreate


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.post("/")
def create_company(
    company: CompanyCreate,
    current_user=Depends(require_role("recruiter")),
    db: Session = Depends(get_db)
):

    new_company = Company(
        recruiter_id=current_user.id,
        name=company.name,
        description=company.description,
        website=company.website,
        location=company.location
    )

    db.add(new_company)

    db.commit()

    db.refresh(new_company)

    return {
        "message": "Company created successfully",
        "company_id": str(new_company.id)
    }


@router.get("/my")
def get_my_companies(
    current_user=Depends(require_role("recruiter")),
    db: Session = Depends(get_db)
):

    companies = (
        db.query(Company)
        .filter(
            Company.recruiter_id == current_user.id
        )
        .all()
    )

    return [
        {
            "id": str(company.id),
            "name": company.name,
            "description": company.description,
            "website": company.website,
            "location": company.location
        }
        for company in companies
    ]