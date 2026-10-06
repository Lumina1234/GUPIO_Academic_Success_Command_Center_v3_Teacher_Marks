from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.security import get_session


def current_user(request: Request, db: Session = Depends(get_db), gupio_session: str | None = Cookie(default=None)) -> User:
    session = get_session(db, gupio_session)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")
    request.state.db_session = session
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return dependency
