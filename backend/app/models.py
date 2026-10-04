from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


class PortfolioException(Base):
    __tablename__ = "exceptions"
    __table_args__ = (
        CheckConstraint(
            "category IN ('Position mismatch', 'Cash variance', "
            "'Unmatched security', 'Stale record')",
            name="ck_exceptions_category",
        ),
        CheckConstraint("priority IN ('High', 'Medium', 'Low')", name="ck_exceptions_priority"),
        CheckConstraint(
            "status IN ('Open', 'Investigating', 'Resolved', 'Dismissed')",
            name="ck_exceptions_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    account: Mapped[str] = mapped_column(String(80), nullable=False)
    household: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="Open")
    age: Mapped[str] = mapped_column(String(24), nullable=False)
    display_value: Mapped[str] = mapped_column(String(32), nullable=False)
    rule: Mapped[str] = mapped_column(String(240), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    checklist: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    evidence: Mapped[list["EvidenceRecord"]] = relationship(
        back_populates="exception",
        cascade="all, delete-orphan",
        order_by="EvidenceRecord.side",
    )
    activities: Mapped[list["ReviewEvent"]] = relationship(
        back_populates="exception",
        cascade="all, delete-orphan",
        order_by="(ReviewEvent.created_at.desc(), ReviewEvent.id.desc())",
    )


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    __table_args__ = (
        CheckConstraint("side IN ('internal', 'external')", name="ck_evidence_side"),
        UniqueConstraint("exception_id", "side", name="uq_evidence_exception_side"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exception_id: Mapped[str] = mapped_column(
        ForeignKey("exceptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[str] = mapped_column(String(32), nullable=False)
    as_of: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False)

    exception: Mapped[PortfolioException] = relationship(back_populates="evidence")


class ReviewEvent(Base):
    __tablename__ = "review_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('detected', 'status_changed')",
            name="ck_review_events_type",
        ),
        CheckConstraint(
            "status IS NULL OR status IN "
            "('Open', 'Investigating', 'Resolved', 'Dismissed')",
            name="ck_review_events_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exception_id: Mapped[str] = mapped_column(
        ForeignKey("exceptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(24), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(24))
    status: Mapped[str | None] = mapped_column(String(24))
    message: Mapped[str] = mapped_column(String(240), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    exception: Mapped[PortfolioException] = relationship(back_populates="activities")
