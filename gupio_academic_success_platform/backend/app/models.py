from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20), default="student")
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", uselist=False)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    csrf_token: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    program: Mapped[str] = mapped_column(String(120), default="AI & Data Science")
    # Year the student is currently in (1, 2, 3 …) and total years in their course
    year: Mapped[int] = mapped_column(Integer, default=1)
    course_duration_years: Mapped[int] = mapped_column(Integer, default=3)
    # Annual averages for completed prior years (null = not yet completed / not recorded)
    year1_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    year2_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    year3_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Current-semester marks
    previous_semester_average: Mapped[float] = mapped_column(Float, default=58)
    current_internal_1: Mapped[float] = mapped_column(Float, default=52)
    current_internal_2: Mapped[float] = mapped_column(Float, default=61)
    assignment_score: Mapped[float] = mapped_column(Float, default=64)
    lab_score: Mapped[float] = mapped_column(Float, default=68)
    attendance_pct: Mapped[float] = mapped_column(Float, default=82)
    backlogs: Mapped[int] = mapped_column(Integer, default=0)
    pass_threshold: Mapped[float] = mapped_column(Float, default=40)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="profile")


class CohortStudent(Base):
    __tablename__ = "cohort_students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_ref: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    section: Mapped[str] = mapped_column(String(20), default="A")
    year: Mapped[int] = mapped_column(Integer, default=1)
    course_duration_years: Mapped[int] = mapped_column(Integer, default=3)
    year1_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    year2_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    year3_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    previous_semester_average: Mapped[float] = mapped_column(Float)
    current_internal_1: Mapped[float] = mapped_column(Float)
    current_internal_2: Mapped[float] = mapped_column(Float)
    assignment_score: Mapped[float] = mapped_column(Float)
    lab_score: Mapped[float] = mapped_column(Float)
    attendance_pct: Mapped[float] = mapped_column(Float)
    backlogs: Mapped[int] = mapped_column(Integer, default=0)
    pass_threshold: Mapped[float] = mapped_column(Float, default=40)


class MarkReport(Base):
    __tablename__ = "mark_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    field_name: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    teacher_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120))
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
