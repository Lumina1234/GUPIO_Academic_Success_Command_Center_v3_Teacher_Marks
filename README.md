# GUPIO Academic Success Command Center

A production-minded React + TypeScript + FastAPI application for the Gupio AI/ML Student Academic Outcome Prediction assignment, extended with a **separate semester-success coaching layer** for teachers and students.

## What problem it solves

The core Gupio workflow predicts a student's final academic outcome as **Dropout / Enrolled / Graduate** using information available at enrollment. The supplied assignment explicitly requires the primary model to exclude the 12 first/second-semester performance variables to prevent leakage. This project preserves that rule in `backend/ml/feature_policy.py` and the training pipeline.

The interactive extension adds a second, clearly separated experience:

- **Semester Success Coach**: uses current internal marks, assignment/lab marks, attendance and previous-semester performance to estimate readiness, identify weak areas and simulate an improvement plan.
- **Cohort Support Simulator**: lets a teacher test a support scenario (for example +5 marks on targeted components) and see how many students cross the configured pass threshold. This is a **scenario estimate, not a causal claim**.
- **Teaching Copilot**: gives targeted actions such as attendance recovery, internal revision, lab practice and previous-semester remediation.

The extension does **not** feed semester marks into the Gupio primary enrollment-time classifier.

## Architecture

```text
React + TypeScript + Vite
        |
        | HTTPS / JSON + HttpOnly session cookie + in-memory CSRF token
        v
FastAPI
  |-- Auth / RBAC / CSRF / Rate limits / Security headers
  |-- Student profile & cohort APIs
  |-- Semester Success Coach (deterministic, documented scenario engine)
  |-- Enrollment ML inference API
        |
        +---- SQLite/PostgreSQL (server-side application data)
        |
        +---- Joblib model artifact
        |
        +---- Audit log
```

## Security design

- Passwords are hashed server-side with Argon2 via `pwdlib`.
- Authentication uses an opaque server-side session token in an `HttpOnly`, `Secure` cookie. User profile data is not stored in browser storage.
- CSRF protection is required on state-changing routes.
- Login is rate-limited by IP and email.
- RBAC protects teacher/admin cohort routes.
- The self profile endpoint is `/api/v1/profile/me`; it does not accept a client-supplied user id.
- Security headers include CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy and Permissions-Policy.
- Admin accounts support TOTP MFA.
- Secrets are environment variables; `.env` is excluded from Git.
- An audit log records important auth/admin events.

For production, put the API behind HTTPS and a WAF (Cloudflare/AWS WAF/Sucuri or equivalent), move rate-limit/session storage to a shared datastore such as Redis, and configure off-site encrypted backups.

## Run locally

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_demo.py
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

### Demo accounts

`backend/scripts/seed_demo.py` creates local development accounts only:

- Student: `student@gupio.local`
- Teacher: `teacher@gupio.local`
- Admin: `admin@gupio.local`

Password is set through `DEMO_PASSWORD` in `.env`. Never use demo credentials in a deployed environment.

The admin TOTP secret is printed once by the seed script. Do not share it.

## Gupio ML training

The panel-supplied `data.csv` is required. The assignment states that the file is semicolon-delimited and that the supplied file should be used unchanged in meaning. Place it at:

```text
data/data.csv
```

Then run:

```bash
cd backend
python -m ml.train
```

The script:

1. loads and inspects the supplied file,
2. strips header whitespace/BOM only,
3. removes the 12 prohibited semester-performance columns,
4. makes a stratified train/test split,
5. compares Logistic Regression and Random Forest using training-fold evaluation,
6. selects the final model using Macro F1,
7. evaluates once on the untouched final test set,
8. stores the complete preprocessing + model pipeline in `backend/models/student_outcome_pipeline.joblib`, and
9. writes actual metrics/feature-importance output under `backend/outputs/`.

No model score, prediction or chart is hard-coded into the application.

## API highlights

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/csrf`
- `GET /api/v1/profile/me`
- `GET /api/v1/coach/me`
- `POST /api/v1/coach/evaluate`
- `POST /api/v1/coach/cohort/simulate`
- `GET /api/v1/ml/model-info`
- `POST /api/v1/ml/predict`
- `GET /api/v1/admin/audit` (admin only)
- `GET /health`

## Important modelling integrity note

The **Gupio primary model remains enrollment-time only**. Semester marks are used only by the separate coaching/scenario module. Keeping these systems separate avoids leaking future academic performance into the required enrollment-time prediction task.

## Test

```bash
cd backend
pytest -q
```

The test suite covers login hashing/session behavior, CSRF, role enforcement, profile access control, coaching calculations and the absence of an insecure user-id profile route.

## Project declaration

AI coding assistants may be used as development aids under the supplied Gupio policy, but the candidate must understand and be able to explain the submitted code, preprocessing, modelling choices and security controls.

## Teacher-entered marks and student correction reports
Semester marks are server-side academic records. Students can view their marks and coaching results but cannot edit or submit marks themselves. Teachers/admins can enter or update a student's marks through the protected Mark Register.

A student who sees an incorrect value can submit a **Mark Correction Report** containing the affected field and an explanation. The report is stored server-side for the teacher/admin to review. Approval/rejection is recorded in the audit log; approval does not let the student change the value.
