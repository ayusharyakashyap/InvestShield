from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# SQLAlchemy Models
class Advisor(Base):
    __tablename__ = "advisors"
    
    id = Column(Integer, primary_key=True, index=True)
    sebi_number = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    firm_name = Column(String)
    registration_date = Column(DateTime)
    validity_date = Column(DateTime)
    status = Column(String)  # Active, Suspended, Cancelled
    location = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    specialization = Column(String)
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class FlaggedContent(Base):
    __tablename__ = "flagged_content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_text = Column(Text)
    source = Column(String)  # WhatsApp, Telegram, Twitter, etc.
    source_url = Column(String, nullable=True)
    fraud_type = Column(String)  # fake_advisor, guaranteed_returns, etc.
    risk_score = Column(Float)
    confidence_score = Column(Float)
    keywords_found = Column(Text)  # JSON string of found keywords
    is_verified_fraud = Column(Boolean, default=False)
    reported_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CorporateAnnouncement(Base):
    __tablename__ = "corporate_announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    announcement_text = Column(Text)
    announcement_date = Column(DateTime)
    source = Column(String)
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String, nullable=True)
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

# Pydantic Models for API
class AdvisorBase(BaseModel):
    sebi_number: Optional[str] = None
    name: Optional[str] = None

class AdvisorVerification(BaseModel):
    sebi_number: Optional[str] = None
    name: Optional[str] = None

class AdvisorResponse(BaseModel):
    id: int
    sebi_number: str
    name: str
    firm_name: str
    status: str
    location: str
    risk_score: float
    is_verified: bool
    verification_details: str
    
    class Config:
        from_attributes = True

class ContentAnalysis(BaseModel):
    text: str
    source: Optional[str] = "manual"
    source_url: Optional[str] = None

class UrlAnalysis(BaseModel):
    url: str
    source: Optional[str] = "web"

class ContentAnalysisResponse(BaseModel):
    risk_score: float
    confidence_score: float
    fraud_type: str
    is_suspicious: bool
    keywords_found: list
    explanation: str
    recommendations: list

class DashboardStats(BaseModel):
    total_advisors: int
    verified_advisors: int
    flagged_content_today: int
    flagged_content_week: int
    top_fraud_types: list
    recent_alerts: list

class FlaggedContentResponse(BaseModel):
    id: int
    content_text: str
    source: str
    fraud_type: str
    risk_score: float
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True
