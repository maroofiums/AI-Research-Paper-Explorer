from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    authors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )