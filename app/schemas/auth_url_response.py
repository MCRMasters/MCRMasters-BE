from pydantic import BaseModel


class AuthUrlResponse(BaseModel):
    auth_url: str
