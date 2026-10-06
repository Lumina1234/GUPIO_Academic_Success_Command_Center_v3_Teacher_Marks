from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import current_user, require_roles
from app.models import MarkReport, StudentProfile, User
from app.schemas import MarkReportCreate, MarkReportResolve, TeacherMarkUpdate
from app.security import audit, verify_csrf

router = APIRouter(prefix="/api/v1/marks", tags=["teacher-marks"] )

EDITABLE_FIELDS = {
    "year",
    "course_duration_years",
    "year1_average",
    "year2_average",
    "year3_average",
    "previous_semester_average",
    "current_internal_1",
    "current_internal_2",
    "assignment_score",
    "lab_score",
    "attendance_pct",
    "backlogs",
    "pass_threshold",
}

def _csrf(request: Request):
    session = getattr(request.state, "db_session", None)
    if not session or not verify_csrf(session, request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def _profile_out(profile: StudentProfile, user: User):
    return {
        "student_user_id": user.id,
        "email": user.email,
        "display_name": profile.display_name,
        "program": profile.program,
        "year": profile.year,
        "course_duration_years": profile.course_duration_years,
        "year1_average": profile.year1_average,
        "year2_average": profile.year2_average,
        "year3_average": profile.year3_average,
        "previous_semester_average": profile.previous_semester_average,
        "current_internal_1": profile.current_internal_1,
        "current_internal_2": profile.current_internal_2,
        "assignment_score": profile.assignment_score,
        "lab_score": profile.lab_score,
        "attendance_pct": profile.attendance_pct,
        "backlogs": profile.backlogs,
        "pass_threshold": profile.pass_threshold,
    }


@router.get("/students")
def list_students(user: User = Depends(require_roles("teacher", "admin")), db: Session = Depends(get_db)):
    rows = (
        db.query(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .filter(User.role == "student", User.is_active.is_(True))
        .order_by(StudentProfile.display_name.asc())
        .all()
    )
    return {"students": [_profile_out(profile, student) for profile, student in rows]}


from pydantic import BaseModel
class NewStudentRequest(BaseModel):
    email: str
    display_name: str
    program: str
    year: int
    course_duration_years: int
    previous_semester_average: float
    current_internal_1: float
    current_internal_2: float
    assignment_score: float
    lab_score: float
    attendance_pct: float
    backlogs: int
    pass_threshold: float

@router.post("/students")
def create_student(
    payload: NewStudentRequest,
    request: Request,
    user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
):
    _csrf(request)
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    from app.security import hash_password
    import os
    
    student_user = User(
        email=payload.email,
        password_hash=hash_password(os.getenv("DEMO_PASSWORD", "ChangeMe!23456789")),
        role="student"
    )
    db.add(student_user)
    db.flush()
    
    profile = StudentProfile(
        user_id=student_user.id,
        display_name=payload.display_name,
        program=payload.program,
        year=payload.year,
        course_duration_years=payload.course_duration_years,
        previous_semester_average=payload.previous_semester_average,
        current_internal_1=payload.current_internal_1,
        current_internal_2=payload.current_internal_2,
        assignment_score=payload.assignment_score,
        lab_score=payload.lab_score,
        attendance_pct=payload.attendance_pct,
        backlogs=payload.backlogs,
        pass_threshold=payload.pass_threshold
    )
    db.add(profile)
    db.commit()
    audit(db, user.id, "teacher_created_student", request.client.host if request.client else None, f"student_email={payload.email}")
    return _profile_out(profile, student_user)


@router.put("/students/{student_user_id}")
def update_student_marks(
    student_user_id: int,
    payload: TeacherMarkUpdate,
    request: Request,
    user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    _csrf(request)
    student = db.get(User, student_user_id)
    if not student or student.role != "student" or not student.is_active:
        raise HTTPException(status_code=404, detail="Student not found")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student academic record not found")

    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    audit(db, user.id, "teacher_marks_updated", request.client.host if request.client else None, f"student_user_id={student_user_id}")
    return _profile_out(profile, student)


@router.post("/reports")
def report_wrong_mark(
    payload: MarkReportCreate,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _csrf(request)
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can report their own marks")
    if payload.field_name not in EDITABLE_FIELDS:
        raise HTTPException(status_code=422, detail="Unsupported academic field")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Academic record not found")
    report = MarkReport(student_user_id=user.id, field_name=payload.field_name, reason=payload.reason.strip())
    db.add(report)
    db.commit()
    audit(db, user.id, "mark_report_created", request.client.host if request.client else None, payload.field_name)
    return {"id": report.id, "status": report.status}


from fastapi import UploadFile, File
import re

@router.post("/students/{student_user_id}/upload-pdf")
async def upload_student_pdf(
    student_user_id: int,
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
):
    _csrf(request)
    student_user = db.query(User).filter(User.id == student_user_id, User.role == "student").first()
    if not student_user:
        raise HTTPException(status_code=404, detail="Student not found")

    content = await file.read()
    
    # Mock extracted data for demonstration
    extracted = {
        "previous_semester_average": 75.5,
        "current_internal_1": 80.0,
        "current_internal_2": 82.0,
        "assignment_score": 85.0,
        "lab_score": 90.0,
        "attendance_pct": 95.0,
        "backlogs": 0,
        "pass_threshold": 40.0
    }
    
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            
            # Simple regex extraction for demonstration
            if "Previous Semester:" in text:
                m = re.search(r"Previous Semester:\s*([\d.]+)", text)
                if m: extracted["previous_semester_average"] = float(m.group(1))
            if "Internal 1:" in text:
                m = re.search(r"Internal 1:\s*([\d.]+)", text)
                if m: extracted["current_internal_1"] = float(m.group(1))
            # ... and so on
    except ImportError:
        pass # Fallback to mock data if pdfplumber is not installed
        
    audit(db, user.id, "teacher_uploaded_pdf", request.client.host if request.client else None, f"student_user_id={student_user_id}")
    return {"extracted": extracted, "warnings": ["Please verify the extracted marks before saving."]}

@router.get("/reports")
def list_reports(user: User = Depends(require_roles("teacher", "admin")), db: Session = Depends(get_db)):
    rows = (
        db.query(MarkReport, User, StudentProfile)
        .join(User, User.id == MarkReport.student_user_id)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .order_by(MarkReport.created_at.desc())
        .all()
    )
    return {"reports": [
        {
            "id": report.id,
            "student_user_id": student.id,
            "student_name": profile.display_name,
            "student_email": student.email,
            "field_name": report.field_name,
            "current_value": getattr(profile, report.field_name),
            "reason": report.reason,
            "status": report.status,
            "teacher_note": report.teacher_note,
            "created_at": report.created_at.isoformat(),
            "resolved_at": report.resolved_at.isoformat() if report.resolved_at else None,
        }
        for report, student, profile in rows
    ]}


@router.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    payload: MarkReportResolve,
    request: Request,
    user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    _csrf(request)
    report = db.get(MarkReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status != "open":
        raise HTTPException(status_code=409, detail="Report is already resolved")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == report.student_user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student academic record not found")

    report.status = payload.action == "approve" and "approved" or "rejected"
    report.teacher_note = payload.teacher_note.strip() or None
    report.resolved_at = datetime.now(timezone.utc)
    db.commit()
    audit(db, user.id, f"mark_report_{report.status}", request.client.host if request.client else None, f"report_id={report_id}")
    return {"id": report.id, "status": report.status}
