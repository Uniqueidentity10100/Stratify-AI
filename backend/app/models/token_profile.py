"""
Token Profile model
Stores user-defined asset sensitivity profiles for unknown tokens
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class TokenProfile(Base):
    """
    Stores custom asset profiles created through conversational fallback
    When asset is not found in CoinGecko, we build sensitivity profile here
    """
    __tablename__ = "token_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Asset identification
    token_name = Column(String, nullable=False)
    token_type = Column(String)  # e.g., "DeFi", "Layer 1", "Meme", "Corporate Stock"
    
    # Sensitivity scores (0.0 to 1.0)
    # Higher score = more sensitive to that factor
    volatility_level = Column(Float, default=0.5)
    liquidity_sensitivity = Column(Float, default=0.5)
    regulation_sensitivity = Column(Float, default=0.5)
    interest_rate_sensitivity = Column(Float, default=0.5)
    geopolitical_sensitivity = Column(Float, default=0.5)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", back_populates="token_profiles")
    
    def __repr__(self):
        return f"<TokenProfile {self.token_name}>"
