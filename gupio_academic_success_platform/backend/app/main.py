import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.models import User
from app.routes import auth, profile, coach, ml, admin, marks

settings = get_settings()
@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    application.state.db_factory = SessionLocal
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' http://localhost:5173 http://127.0.0.1:5173; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
    if settings.cookie_secure or settings.app_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.exception_handler(Exception)
async def unhandled_error(_, exc):
    # Do not leak stack traces or implementation details to clients.
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(coach.router)
app.include_router(ml.router)
app.include_router(admin.router)
app.include_router(marks.router)
