
def login(client, email="student@test.local"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass!123456"})
    assert response.status_code == 200, response.text
    body = response.json()
    return body["csrf_token"]


def test_password_is_not_returned_and_profile_is_self_scoped(client):
    csrf = login(client)
    profile = client.get("/api/v1/profile/me")
    assert profile.status_code == 200
    assert "password" not in profile.text.lower()
    assert profile.json()["user"]["email"] == "student@test.local"
    # There is intentionally no /profile/{id} route to exploit through URL tampering.
    assert client.get("/api/v1/profile/1").status_code == 404
    assert client.get("/api/v1/profile/2").status_code == 404


def test_csrf_required_for_state_change(client):
    login(client)
    response = client.post("/api/v1/coach/evaluate", json={
        "previous_semester_average": 50,
        "current_internal_1": 50,
        "current_internal_2": 50,
        "assignment_score": 50,
        "lab_score": 50,
        "attendance_pct": 80,
        "backlogs": 0,
        "pass_threshold": 40,
    })
    assert response.status_code == 403


def test_coach_returns_transparent_actions(client):
    csrf = login(client)
    response = client.post("/api/v1/coach/evaluate", headers={"X-CSRF-Token": csrf}, json={
        "previous_semester_average": 35,
        "current_internal_1": 30,
        "current_internal_2": 35,
        "assignment_score": 34,
        "lab_score": 38,
        "attendance_pct": 70,
        "backlogs": 1,
        "pass_threshold": 40,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["support_needed"] in {"High", "Very high", "Moderate"}
    assert body["weak_areas"]
    assert body["teaching_actions"]
    assert "causal" in body["scenario_note"].lower()


def test_student_cannot_read_cohort(client):
    login(client)
    assert client.get("/api/v1/coach/cohort").status_code == 403


def test_logout_invalidates_session(client):
    login(client)
    assert client.get("/api/v1/profile/me").status_code == 200
    assert client.post("/api/v1/auth/logout", json={}).status_code == 200
    assert client.get("/api/v1/profile/me").status_code == 401


def login_as(client, email):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass!123456"})
    assert response.status_code == 200, response.text
    return response.json()["csrf_token"]


def test_student_marks_are_read_only_and_can_report(client):
    csrf = login_as(client, "student@test.local")
    blocked = client.put("/api/v1/marks/students/1", headers={"X-CSRF-Token": csrf}, json={
        "previous_semester_average": 90, "current_internal_1": 90, "current_internal_2": 90,
        "assignment_score": 90, "lab_score": 90, "attendance_pct": 90, "backlogs": 0, "pass_threshold": 40
    })
    assert blocked.status_code == 403
    report = client.post("/api/v1/marks/reports", headers={"X-CSRF-Token": csrf}, json={
        "field_name": "current_internal_1",
        "reason": "The internal 1 mark displayed in the portal is incorrect."
    })
    assert report.status_code == 200


def test_teacher_can_update_marks_and_resolve_report(client):
    csrf = login_as(client, "teacher@test.local")
    students = client.get("/api/v1/marks/students")
    assert students.status_code == 200
    student = next(s for s in students.json()["students"] if s["email"] == "student@test.local")
    updated = dict(student)
    updated["current_internal_1"] = 66
    updated.pop("student_user_id", None); updated.pop("email", None); updated.pop("display_name", None); updated.pop("program", None); updated.pop("year", None)
    response = client.put(f"/api/v1/marks/students/{student['student_user_id']}", headers={"X-CSRF-Token": csrf}, json=updated)
    assert response.status_code == 200
    reports = client.get("/api/v1/marks/reports")
    assert reports.status_code == 200
    open_reports = [r for r in reports.json()["reports"] if r["status"] == "open"]
    assert open_reports
    resolved = client.post(f"/api/v1/marks/reports/{open_reports[0]['id']}/resolve", headers={"X-CSRF-Token": csrf}, json={"action":"approve","teacher_note":"Verified against the teacher register and corrected."})
    assert resolved.status_code == 200
