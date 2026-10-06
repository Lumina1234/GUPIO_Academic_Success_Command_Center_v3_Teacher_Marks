from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.coaching import evaluate, simulate
from app.db import get_db
from app.dependencies import current_user, require_roles
from app.models import CohortStudent, StudentProfile, User
from app.schemas import CoachMetrics, CohortSimulationRequest
from app.security import audit, verify_csrf

router = APIRouter(prefix="/api/v1/coach", tags=["semester-coach"])


def _csrf(request: Request):
    session = getattr(request.state, "db_session", None)
    if not session or not verify_csrf(session, request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


@router.get("/me")
def coach_me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No academic profile configured")
    metrics = {
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
    return {"name": profile.display_name, "metrics": metrics, "analysis": evaluate(metrics).__dict__}


@router.post("/evaluate")
def evaluate_current(payload: CoachMetrics, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _csrf(request)
    result = evaluate(payload.model_dump())
    audit(db, user.id, "coach_evaluation", request.client.host if request.client else None, None)
    return result.__dict__


@router.get("/cohort")
def cohort(user: User = Depends(require_roles("teacher", "admin")), db: Session = Depends(get_db)):
    rows = db.query(CohortStudent).order_by(CohortStudent.section, CohortStudent.name).all()
    return {
        "students": [
            {
                "public_ref": row.public_ref,
                "name": row.name,
                "section": row.section,
                "year": row.year,
                "course_duration_years": row.course_duration_years,
                "year1_average": row.year1_average,
                "year2_average": row.year2_average,
                "year3_average": row.year3_average,
                "previous_semester_average": row.previous_semester_average,
                "current_internal_1": row.current_internal_1,
                "current_internal_2": row.current_internal_2,
                "assignment_score": row.assignment_score,
                "lab_score": row.lab_score,
                "attendance_pct": row.attendance_pct,
                "backlogs": row.backlogs,
                "pass_threshold": row.pass_threshold,
                "analysis": evaluate({
                    "year": row.year,
                    "course_duration_years": row.course_duration_years,
                    "year1_average": row.year1_average,
                    "year2_average": row.year2_average,
                    "year3_average": row.year3_average,
                    "previous_semester_average": row.previous_semester_average,
                    "current_internal_1": row.current_internal_1,
                    "current_internal_2": row.current_internal_2,
                    "assignment_score": row.assignment_score,
                    "lab_score": row.lab_score,
                    "attendance_pct": row.attendance_pct,
                    "backlogs": row.backlogs,
                    "pass_threshold": row.pass_threshold,
                }).__dict__,
            }
            for row in rows
        ]
    }


@router.post("/cohort/simulate")
def cohort_simulate(payload: CohortSimulationRequest, request: Request, user: User = Depends(require_roles("teacher", "admin")), db: Session = Depends(get_db)):
    _csrf(request)
    rows = db.query(CohortStudent).all()
    data = [
        {
            "public_ref": row.public_ref,
            "name": row.name,
            "year": row.year,
            "course_duration_years": row.course_duration_years,
            "year1_average": row.year1_average,
            "year2_average": row.year2_average,
            "year3_average": row.year3_average,
            "previous_semester_average": row.previous_semester_average,
            "current_internal_1": row.current_internal_1,
            "current_internal_2": row.current_internal_2,
            "assignment_score": row.assignment_score,
            "lab_score": row.lab_score,
            "attendance_pct": row.attendance_pct,
            "backlogs": row.backlogs,
            "pass_threshold": row.pass_threshold,
        }
        for row in rows
    ]
    result = simulate(data, payload.support_marks, payload.attendance_uplift, payload.target_threshold)
    audit(db, user.id, "cohort_scenario", request.client.host if request.client else None, None)
    return result
