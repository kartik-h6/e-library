"""Password hashing, session helpers, role checks.

Deliberately dependency-free: PBKDF2-HMAC-SHA256 from the standard library.
Authorisation is always enforced on the server (see ADR-003).
"""
import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request, status

from .models import User

_ITER = 200_000


def hash_password(password: str, *, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITER)
    return f"pbkdf2_sha256${_ITER}${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt, digest = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iters))
        return hmac.compare_digest(dk.hex(), digest)
    except Exception:
        return False


# ---------------------------------------------------------------- session

def login_session(request: Request, user: User) -> None:
    request.session["uid"] = user.id
    request.session["csrf"] = secrets.token_urlsafe(24)


def logout_session(request: Request) -> None:
    request.session.clear()


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(24)
        request.session["csrf"] = token
    return token


def check_csrf(request: Request, token: str | None) -> None:
    if not token or token != request.session.get("csrf"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")


def current_user(request: Request, db) -> User | None:
    uid = request.session.get("uid")
    if not uid:
        return None
    return db.get(User, uid)


def require_user(request: Request, db) -> User:
    user = current_user(request, db)
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


# ---------------------------------------------------------------- permissions

def is_student(user: User) -> bool:
    """The shared student account — read-only access to published material."""
    return user.role == "student"


def can_manage_subjects(user: User) -> bool:
    return user.role in ("super_admin", "hod")


def can_edit_resources(user: User) -> bool:
    return user.role in ("super_admin", "hod", "sme", "contributor")


def can_approve(user: User) -> bool:
    return user.role in ("super_admin", "hod")


def can_publish(user: User) -> bool:
    return user.role in ("super_admin", "hod")


def in_scope(user: User, subject) -> bool:
    """A user acts on a subject if they are a super admin, or it belongs to their department."""
    if user.role == "super_admin":
        return True
    return subject.department_id is not None and subject.department_id == user.department_id
