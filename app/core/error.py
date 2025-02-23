from enum import Enum
from typing import Any


class DomainErrorCode(str, Enum):
    INVALID_UID = "INVALID_UID"


class MCRDomainError(Exception):
    def __init__(
        self,
        code: DomainErrorCode,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message or code.name
        self.details = details or {}
        super().__init__(self.message)
