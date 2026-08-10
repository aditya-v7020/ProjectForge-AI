"""ProjectForge AI — Security Utilities.

Password hashing (bcrypt) and JWT token management.
"""
import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from backend.app.core import settings


def _preprocess_password(password: str) -> bytes:
    """Pre-process a password using SHA-256 to ensure standard fixed-length input for bcrypt.
    
    This avoids bcrypt's 72-byte limit and handles Unicode strings seamlessly.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    """Hash a password securely using SHA-256 pre-hashing and bcrypt."""
    processed = _preprocess_password(password)
    hashed = bcrypt.hashpw(processed, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash with backward compatibility for legacy hashes."""
    if not plain_password or not hashed_password:
        return False

    hashed_bytes = hashed_password.encode("utf-8")

    # Primary check: SHA-256 pre-hashed verification
    try:
        processed = _preprocess_password(plain_password)
        if bcrypt.checkpw(processed, hashed_bytes):
            return True
    except Exception:
        pass

    # Legacy check: Direct bcrypt verification for passwords hashed before pre-hashing
    try:
        raw_bytes = plain_password.encode("utf-8")
        if len(raw_bytes) <= 72:
            if bcrypt.checkpw(raw_bytes, hashed_bytes):
                return True
    except Exception:
        pass

    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
