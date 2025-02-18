import bcrypt


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")  # type: ignore[no-any-return]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(  # type: ignore[no-any-return]
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
