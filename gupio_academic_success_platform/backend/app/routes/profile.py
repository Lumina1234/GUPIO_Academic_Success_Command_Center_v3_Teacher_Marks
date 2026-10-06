from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import current_user
from app.models import StudentProfile, User

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("/me")
def get_my_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    return {
        "user": {"email": user.email, "role": user.role, "mfa_enabled": user.mfa_enabled},
        "profile": None if not profile else {
            "display_name": profile.display_name,
            "program": profile.program,
            "year": profile.year,
            "previous_semester_average": profile.previous_semester_average,
            "current_internal_1": profile.current_internal_1,
            "current_internal_2": profile.current_internal_2,
            "assignment_score": profile.assignment_score,
            "lab_score": profile.lab_score,
            "attendance_pct": profile.attendance_pct,
            "backlogs": profile.backlogs,
            "pass_threshold": profile.pass_threshold,
            "marks_source": "teacher_entered",
        },
    }
