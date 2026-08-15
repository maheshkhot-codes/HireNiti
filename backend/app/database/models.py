from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


# =========================================================
# USER
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=True
    )

    role = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =========================================================
# IMPORT ALL OTHER MODELS
# =========================================================

from app.candidates.models import CandidateProfile
from app.recruiters.models import RecruiterProfile
from app.companies.models import Company
from app.jobs.models import Job
from app.resume.models import Resume
from app.applications.models import Application