from ml.feature_policy import PROHIBITED_SEMESTER_COLUMNS


def test_exactly_twelve_prohibited_semester_fields():
    assert len(PROHIBITED_SEMESTER_COLUMNS) == 12
    assert "Curricular units 1st sem (grade)" in PROHIBITED_SEMESTER_COLUMNS
    assert "Curricular units 2nd sem (grade)" in PROHIBITED_SEMESTER_COLUMNS
