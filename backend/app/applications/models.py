from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base



class Application(Base):

    __tablename__ = "applications"

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

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="applied"
    )

    applied_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )