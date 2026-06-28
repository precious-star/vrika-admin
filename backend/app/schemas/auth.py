"""Auth schemas for Vrika Admin."""

from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=256)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: str
    email: str
    username: str
    tenant_id: str
    roles: list[str]
    organization_name: str = ""
