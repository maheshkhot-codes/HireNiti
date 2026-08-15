from sqlalchemy import Column, String, Text, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class CandidateProfile(Base):

    __tablename__ = "candidate_profiles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    phone = Column(String(20))

    location = Column(String(150))

    skills = Column(Text)

    education = Column(Text)

    experience_years = Column(Numeric(4, 1))

    bio = Column(Text)