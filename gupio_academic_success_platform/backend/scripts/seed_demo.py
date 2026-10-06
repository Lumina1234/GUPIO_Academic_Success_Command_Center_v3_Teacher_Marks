import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import Base, SessionLocal, engine
from app.models import CohortStudent, StudentProfile, User
from app.security import hash_password, new_totp_secret

Base.metadata.create_all(bind=engine)
db = SessionLocal()
password = os.getenv("DEMO_PASSWORD", "ChangeMe!23456789")


def get_or_create(email, role, name):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash=hash_password(password), role=role)
        db.add(user)
        db.flush()
    return user

student = get_or_create("student@gupio.local", "student", "Demo Student")
teacher = get_or_create("teacher@gupio.local", "teacher", "Demo Teacher")
admin = get_or_create("admin@gupio.local", "admin", "Demo Admin")
if not admin.totp_secret:
    admin.totp_secret = new_totp_secret()
admin.mfa_enabled = True

if not student.profile:
    db.add(StudentProfile(
        user_id=student.id,
        display_name="Demo Student",
        previous_semester_average=58,
        current_internal_1=52,
        current_internal_2=61,
        assignment_score=64,
        lab_score=68,
        attendance_pct=82,
        backlogs=0,
        pass_threshold=40,
    ))

if db.query(CohortStudent).count() == 0:
    sample = [
        ("Aarav", "A", 71, 68, 74, 80, 83, 91, 0),
        ("Bhavana", "A", 52, 44, 49, 55, 51, 78, 0),
        ("Charan", "A", 39, 42, 37, 45, 44, 72, 1),
        ("Diya", "A", 64, 58, 62, 69, 71, 84, 0),
        ("Eshan", "A", 46, 38, 41, 43, 39, 69, 1),
        ("Farah", "B", 73, 79, 82, 77, 88, 95, 0),
        ("Gagan", "B", 55, 57, 51, 49, 53, 76, 0),
        ("Hema", "B", 42, 35, 40, 38, 41, 80, 1),
        ("Ishan", "B", 61, 63, 59, 66, 62, 88, 0),
        ("Jhanvi", "B", 49, 46, 48, 51, 47, 73, 0),
        ("Kiran", "C", 36, 31, 39, 35, 37, 64, 2),
        ("Leela", "C", 68, 70, 67, 72, 76, 90, 0),
    ]
    for name, section, prev, i1, i2, assn, lab, att, backlogs in sample:
        db.add(CohortStudent(
            public_ref=str(uuid.uuid4()),
            name=name,
            section=section,
            previous_semester_average=prev,
            current_internal_1=i1,
            current_internal_2=i2,
            assignment_score=assn,
            lab_score=lab,
            attendance_pct=att,
            backlogs=backlogs,
            pass_threshold=40,
        ))

db.commit()
print("Demo accounts seeded.")
print("Student:", student.email)
print("Teacher:", teacher.email)
print("Admin:", admin.email)
print("Admin TOTP secret (keep private):", admin.totp_secret)
db.close()
