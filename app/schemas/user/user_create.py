from pydantic import BaseModel, field_validator

from app.util.validators import validate_password, validate_username


class UserCreate(BaseModel):
    username: str
    password: str

    @classmethod
    @field_validator("username")
    def username_validator(cls, username: str) -> str:
        return validate_username(username)

    @classmethod
    @field_validator("password")
    def password_validator(cls, password: str) -> str:
        return validate_password(password)
