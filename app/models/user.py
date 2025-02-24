from datetime import datetime

from pydantic import field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import Field

from app.models.base_model import BaseModel
from app.util.validators import validate_uid


class User(BaseModel, table=True):  # type: ignore[call-arg]
    uid: str = Field(index=True, unique=True)
    nickname: str = Field(max_length=10)
    is_active: bool = Field(default=True)
    last_login: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    email: str | None = Field(default=None)

    @field_validator("uid")
    @classmethod
    def validate_uid(cls, v: str) -> str:
        return validate_uid(v)
