
def login_teacher(client):
    r = client.post("/api/v1/auth/login", json={"email":"teacher@test.local","password":"StrongPass!123456"})
    assert r.status_code == 200
    return r.json()["csrf_token"]


def test_teacher_can_simulate_cohort_and_result_is_scenario(client):
    csrf = login_teacher(client)
    r = client.post("/api/v1/coach/cohort/simulate", headers={"X-CSRF-Token":csrf}, json={"support_marks":5,"attendance_uplift":3})
    assert r.status_code == 200
    body = r.json()
    assert body["total_students"] == 1
    assert body["supported_pass_count"] >= body["baseline_pass_count"]
    assert "not evidence" in body["note"].lower()
