"""
Report model
Stores generated probability reports and analysis results
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Report(Base):
    """
    Stores generated analysis reports
    Each report contains probability scores and narrative
    """
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Asset analyzed
    token_name = Column(String, nullable=False)
    
    # Probability scores (0.0 to 1.0)
    short_term_prob = Column(Float)  # 0-4 weeks
    medium_term_prob = Column(Float)  # 1-6 months
    long_term_prob = Column(Float)  # 6-24 months
    
    # Analysis narrative
    short_term_narrative = Column(Text)
    medium_term_narrative = Column(Text)
    long_term_narrative = Column(Text)
    most_likely_scenario = Column(Text)
    
    # Confidence level
    confidence_level = Column(String)  # "High", "Medium", "Low"
    
    # PDF storage path (optional)
    pdf_path = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report {self.token_name} - {self.created_at.date()}>"
