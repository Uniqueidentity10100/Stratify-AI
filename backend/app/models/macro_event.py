"""
Macro Event model
Stores significant macroeconomic events and their scores
"""
from sqlalchemy import Column, String, Float, DateTime, Text
from datetime import datetime
import uuid

from app.database import Base


class MacroEvent(Base):
    """
    Stores macro events that influence assets
    Each event has severity, sentiment, and classification
    """
    __tablename__ = "macro_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event classification
    event_type = Column(String, nullable=False)  # e.g., "interest_rate", "regulation", "geopolitical"
    event_description = Column(Text)
    
    # Event scoring
    severity_score = Column(Float, default=0.5)  # 0.0 to 1.0 - how significant
    sentiment_score = Column(Float, default=0.5)  # 0.0 (very negative) to 1.0 (very positive)
    recency_score = Column(Float, default=1.0)  # Decays over time
    attention_score = Column(Float, default=0.5)  # Media/market attention level
    
    # Metadata
    source = Column(String)  # e.g., "FRED", "NewsAPI", "Manual"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MacroEvent {self.event_type}: {self.event_description[:50]}>"
