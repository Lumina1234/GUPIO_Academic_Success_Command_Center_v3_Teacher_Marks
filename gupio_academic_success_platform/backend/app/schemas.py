from typing import Any
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=12, max_length=256)
    otp: str | None = Field(default=None, min_length=6, max_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email")
        return value


class UserOut(BaseModel):
    email: str
    role: str
    mfa_enabled: bool


class LoginResponse(BaseModel):
    user: UserOut
    csrf_token: str


class CoachMetrics(BaseModel):
    year: int = Field(default=1, ge=1, le=10)
    course_duration_years: int = Field(default=3, ge=1, le=10)
    year1_average: float | None = Field(default=None, ge=0, le=100)
    year2_average: float | None = Field(default=None, ge=0, le=100)
    year3_average: float | None = Field(default=None, ge=0, le=100)
    previous_semester_average: float = Field(ge=0, le=100)
    current_internal_1: float = Field(ge=0, le=100)
    current_internal_2: float = Field(ge=0, le=100)
    assignment_score: float = Field(ge=0, le=100)
    lab_score: float = Field(ge=0, le=100)
    attendance_pct: float = Field(ge=0, le=100)
    backlogs: int = Field(ge=0, le=20)
    pass_threshold: float = Field(default=40, ge=0, le=100)


class CohortSimulationRequest(BaseModel):
    support_marks: float = Field(ge=0, le=20)
    attendance_uplift: float = Field(default=0, ge=0, le=15)
    target_threshold: float | None = Field(default=None, ge=0, le=100)


class PredictionRequest(BaseModel):
    features: dict[str, Any]


class TeacherMarkUpdate(BaseModel):
    year: int = Field(default=1, ge=1, le=10)
    course_duration_years: int = Field(default=3, ge=1, le=10)
    year1_average: float | None = Field(default=None, ge=0, le=100)
    year2_average: float | None = Field(default=None, ge=0, le=100)
    year3_average: float | None = Field(default=None, ge=0, le=100)
    previous_semester_average: float = Field(ge=0, le=100)
    current_internal_1: float = Field(ge=0, le=100)
    current_internal_2: float = Field(ge=0, le=100)
    assignment_score: float = Field(ge=0, le=100)
    lab_score: float = Field(ge=0, le=100)
    attendance_pct: float = Field(ge=0, le=100)
    backlogs: int = Field(ge=0, le=20)
    pass_threshold: float = Field(ge=0, le=100)


class MarkReportCreate(BaseModel):
    field_name: str = Field(min_length=2, max_length=64)
    reason: str = Field(min_length=5, max_length=1000)


class MarkReportResolve(BaseModel):
    action: str = Field(pattern=r"^(approve|reject)$")
    teacher_note: str = Field(default="", max_length=1000)
