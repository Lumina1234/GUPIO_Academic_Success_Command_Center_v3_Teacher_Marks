# Verification record

## Backend

- Python syntax compilation: PASS
- Automated backend tests: **7 passed**
- Test coverage includes authentication/session behavior, CSRF enforcement, profile self-scope/URL-tampering resistance, student/teacher role enforcement, coaching output, cohort scenario behavior and exact 12-field leakage policy.

## Frontend

The source is included as a React + TypeScript + Vite application. A local `npm install`/build could not be completed in this execution environment because the package registry connection timed out. No fabricated frontend build result is claimed.

## ML dataset

The panel-supplied `data.csv` was not available in the uploaded files for this build, so no ML scores, predictions or evaluation charts have been fabricated. Place the official supplied file in `data/data.csv` and run `python -m ml.train` to create the real pipeline and actual evaluation outputs.


### Mark ownership loop
- Student: marks are read-only.
- Student: can report an incorrect mark with an explanation.
- Teacher/Admin: can enter or update marks.
- Teacher/Admin: can review and resolve correction reports.
- Mark changes are server-side and audited.
