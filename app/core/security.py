from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings


def get_password_hash(password: str) -> str:
    password_bytes: bytes = password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(
        bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        ),
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    to_encode.update({"exp": expire})

    encoded_token = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return str(encoded_token)


def create_refresh_token(data: dict) -> str:
    return create_access_token(
        data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return dict(payload)
    except JWTError:
        return None


def get_username_from_token(token: str) -> str | None:
    payload = decode_token(token)
    return payload.get("sub") if payload else None
