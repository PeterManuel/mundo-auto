from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field, EmailStr


class TokenPayload(BaseModel):
    user_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginCredentials(BaseModel):
    username: str = Field(..., description="Email address used as username")
    password: str = Field(..., min_length=8)


class PasswordReset(BaseModel):
    email: str


class PasswordUpdate(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v