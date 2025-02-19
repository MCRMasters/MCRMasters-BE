from pydantic import BaseModel, field_validator

from app.util.validators import validate_password, validate_username


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_validator(cls, v: str) -> str:
        return validate_username(v)

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: str) -> str:
        return validate_password(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
