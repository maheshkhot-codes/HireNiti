from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    DateTime,
    text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base
from pgvector.sqlalchemy import Vector


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_url = Column(Text)
    embedding = Column(
    Vector(384)
)

    parsed_text = Column(Text)

    skills = Column(Text)

    education = Column(Text)

    experience = Column(Text)
    projects = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )