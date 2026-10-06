import base64
import hashlib
import hmac
import secrets
import struct
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import AuditEvent, Session as DbSession, User

settings = get_settings()
SESSION_COOKIE = "gupio_session"

# Memory-hard password hashing using Python's standard-library scrypt.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
KEY_LEN = 64


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=KEY_LEN)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_hex, digest_hex = encoded.split("$", 5)
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=len(bytes.fromhex(digest_hex)))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _hash_token(token: str) -> str:
    return hashlib.sha256((settings.app_secret_key + token).encode()).hexdigest()


def create_session(db: Session, user: User, ip: str | None) -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    session = DbSession(
        token_hash=_hash_token(raw),
        user_id=user.id,
        csrf_token=csrf,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours),
        last_ip=ip,
    )
    db.add(session)
    db.commit()
    return raw, csrf


def get_session(db: Session, raw_token: str | None) -> DbSession | None:
    if not raw_token:
        return None
    session = db.query(DbSession).filter(DbSession.token_hash == _hash_token(raw_token)).first()
    if not session:
        return None
    # SQLite may return a naive datetime; treat it as UTC for comparison.
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None
    return session


def destroy_session(db: Session, raw_token: str | None) -> None:
    session = get_session(db, raw_token)
    if session:
        db.delete(session)
        db.commit()


def verify_csrf(session: DbSession, presented: str | None) -> bool:
    if not presented:
        return False
    return hmac.compare_digest(session.csrf_token, presented)


def audit(db: Session, actor_user_id: int | None, action: str, ip: str | None, metadata: str | None = None):
    db.add(AuditEvent(actor_user_id=actor_user_id, action=action, ip_address=ip, metadata_json=metadata))
    db.commit()


def new_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def totp_code(secret: str, for_time: int | None = None) -> str:
    now = int(time.time()) if for_time is None else int(for_time)
    counter = now // 30
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset+4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    try:
        code = str(code).strip()
        now = int(time.time())
        for delta in range(-window, window + 1):
            if hmac.compare_digest(totp_code(secret, now + delta * 30), code):
                return True
        return False
    except Exception:
        return False
