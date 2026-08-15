from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    DateTime
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class Company(Base):

    __tablename__ = "companies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    recruiter_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        )
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text
    )

    website = Column(
        String(255)
    )

    location = Column(
        String(150)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )