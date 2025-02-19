from app.core.error import DomainErrorCode, MCRDomainError

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20


def validate_username(username: str) -> str:
    if not MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH:
        raise MCRDomainError(
            code=DomainErrorCode.INVALID_USERNAME,
            message="username length is invalid",
            details={
                "length": len(username),
                "min_length": MIN_USERNAME_LENGTH,
                "max_length": MAX_USERNAME_LENGTH,
            },
        )
    return username


MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 20


def validate_password(password: str) -> str:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise MCRDomainError(
            code=DomainErrorCode.INVALID_PASSWORD,
            message="password length is invalid",
            details={
                "length": len(password),
                "min_length": MIN_PASSWORD_LENGTH,
                "max_length": MAX_PASSWORD_LENGTH,
            },
        )
    return password
