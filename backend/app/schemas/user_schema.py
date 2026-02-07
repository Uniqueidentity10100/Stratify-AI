"""
User schemas for request and response validation
Uses Pydantic for automatic validation
"""
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for user registration
    Validates email format and password requirements
    """
    email: EmailStr
    password: str  # Will be hashed before storage
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "analyst@stratify.ai",
                "password": "SecurePassword123!"
            }
        }


class UserResponse(BaseModel):
    """
    Schema for user data in responses
    Never includes password or sensitive data
    """
    id: UUID4
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    Schema for login requests
    """
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "analyst@stratify.ai",
                "password": "SecurePassword123!"
            }
        }
