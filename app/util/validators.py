import re

from app.core.error import DomainErrorCode, MCRDomainError


def validate_uid(uid: str) -> str:
    if not re.match(r"^[1-9]\d{8}$", uid):
        raise MCRDomainError(
            code=DomainErrorCode.INVALID_UID,
            message="UID must be a 9-digit number",
            details={
                "uid": uid,
            },
        )
    return uid
