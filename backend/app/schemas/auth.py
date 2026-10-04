from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


class Registration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=3,
            max_length=150,
            pattern=r"^[a-zA-Z0-9_.@+-]+$",
        ),
    ]
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=10, max_length=128)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    date_joined: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class MessageResponse(BaseModel):
    detail: str
