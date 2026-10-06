from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.models import User
from app.rate_limit import limiter
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.security import SESSION_COOKIE, audit, create_session, destroy_session, get_session, verify_csrf, verify_password, verify_totp

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
settings = get_settings()


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    allowed_ip = limiter.allow(f"ip:{ip}", settings.login_rate_limit, settings.login_rate_window_seconds)
    allowed_email = limiter.allow(f"email:{str(payload.email).lower()}", settings.login_rate_limit, settings.login_rate_window_seconds)
    if not (allowed_ip and allowed_email):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    email = str(payload.email).lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        audit(db, None, "login_failed", ip, '{"reason":"invalid_credentials"}')
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role == "admin" and user.mfa_enabled:
        if not payload.otp or not user.totp_secret or not verify_totp(user.totp_secret, payload.otp, window=1):
            audit(db, user.id, "login_failed_mfa", ip, None)
            raise HTTPException(status_code=401, detail="MFA required or invalid")

    token, csrf = create_session(db, user, ip)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_ttl_hours * 3600,
        path="/",
    )
    audit(db, user.id, "login_success", ip, None)
    return LoginResponse(user=UserOut(email=user.email, role=user.role, mfa_enabled=user.mfa_enabled), csrf_token=csrf)


@router.get("/csrf")
def csrf(request: Request, gupio_session: str | None = None, db: Session = Depends(get_db)):
    # Kept for documentation; the actual session is read from the Cookie dependency below in production.
    from fastapi import Cookie
    raise HTTPException(status_code=401, detail="Use the /login response csrf_token or authenticated cookie")


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw = request.cookies.get(SESSION_COOKIE)
    session = get_session(db, raw)
    if session:
        audit(db, session.user_id, "logout", _client_ip(request), None)
    destroy_session(db, raw)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    raw = request.cookies.get(SESSION_COOKIE)
    session = get_session(db, raw)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"user": UserOut(email=user.email, role=user.role, mfa_enabled=user.mfa_enabled), "csrf_token": session.csrf_token}


@router.post("/verify-csrf")
def verify_csrf_endpoint(request: Request, db: Session = Depends(get_db)):
    raw = request.cookies.get(SESSION_COOKIE)
    session = get_session(db, raw)
    if not session or not verify_csrf(session, request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    return {"ok": True}
