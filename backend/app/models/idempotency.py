from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    operation: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    request_hash: Mapped[str] = mapped_column(
        String(64)
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="in_progress",
    )

    response_json: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow,
        )
    )

    updated_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
        )
    )