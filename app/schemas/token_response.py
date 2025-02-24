from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool
    token_type: str = "bearer"
