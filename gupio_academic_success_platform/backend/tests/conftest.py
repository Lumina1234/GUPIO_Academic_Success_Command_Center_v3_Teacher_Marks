import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
TEST_DB = Path(__file__).resolve().parent / "test_gupio.db"
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["APP_SECRET_KEY"] = "test-secret-key-with-enough-length"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"
os.environ["COOKIE_SECURE"] = "false"
os.environ["APP_ENV"] = "test"
os.environ["LOGIN_RATE_LIMIT"] = "50"

import pytest
from fastapi.testclient import TestClient
from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import User, StudentProfile, CohortStudent
from app.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    student = User(email="student@test.local", password_hash=hash_password("StrongPass!123456"), role="student")
    teacher = User(email="teacher@test.local", password_hash=hash_password("StrongPass!123456"), role="teacher")
    db.add_all([student, teacher])
    db.flush()
    db.add(StudentProfile(user_id=student.id, display_name="Test Student", previous_semester_average=55, current_internal_1=45, current_internal_2=50, assignment_score=52, lab_score=60, attendance_pct=80, backlogs=0, pass_threshold=40))
    student2 = User(email="student2@test.local", password_hash=hash_password("StrongPass!123456"), role="student")
    db.add(student2)
    db.flush()
    db.add(StudentProfile(user_id=student2.id, display_name="Second Student", previous_semester_average=62, current_internal_1=58, current_internal_2=60, assignment_score=65, lab_score=67, attendance_pct=88, backlogs=0, pass_threshold=40))
    db.add(CohortStudent(public_ref="student-public-ref", name="Test Cohort Student", section="A", previous_semester_average=35, current_internal_1=35, current_internal_2=35, assignment_score=38, lab_score=40, attendance_pct=70, backlogs=1, pass_threshold=40))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if TEST_DB.exists(): TEST_DB.unlink()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
