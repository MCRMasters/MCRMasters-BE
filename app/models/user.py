from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field

from app.core.security import verify_password
from app.models.base_model import BaseModel


class User(BaseModel, table=True):  # type: ignore[call-arg]
    username: str | None = Field(unique=True, default=None)
    password_hash: str
    is_active: bool = Field(default=True)
    last_login: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password_hash)
