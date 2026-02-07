"""
Security utilities for password hashing
Uses bcrypt for secure password storage
"""
from passlib.context import CryptContext

# Create password hashing context
# bcrypt is industry standard for password hashing
# Automatically handles salting and multiple rounds
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    
    Args:
        password: Plain text password from user
        
    Returns:
        Hashed password safe for database storage
        
    Example:
        hashed = hash_password("mypassword123")
        # Returns: $2b$12$KIXqX... (60 character hash)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Password entered by user
        hashed_password: Hash stored in database
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("mypassword123", stored_hash)
    """
    return pwd_context.verify(plain_password, hashed_password)
