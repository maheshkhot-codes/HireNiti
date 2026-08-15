from sqlalchemy import Column, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base
from pgvector.sqlalchemy import Vector

class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True
    )

    recruiter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    embedding = Column(
    Vector(384)
)

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    required_skills = Column(Text)

    preferred_skills = Column(Text)

    experience_min = Column(Numeric(4, 1))

    experience_max = Column(Numeric(4, 1))

    education = Column(String(200))

    location = Column(String(150))

    employment_type = Column(String(50))

    salary_min = Column(Numeric(12, 2))

    salary_max = Column(Numeric(12, 2))

    status = Column(
        String(30),
        default="draft"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )