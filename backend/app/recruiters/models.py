from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class RecruiterProfile(Base):

    __tablename__ = "recruiter_profiles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    company_name = Column(String(200))

    designation = Column(String(100))

    phone = Column(String(20))