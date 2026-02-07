"""
Authentication schemas for JWT token handling
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Schema for JWT token response
    """
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Schema for decoded token data
    Contains user identification from JWT payload
    """
    email: Optional[str] = None
    user_id: Optional[str] = None
