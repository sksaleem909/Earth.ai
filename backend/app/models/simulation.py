from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    traffic_score = Column(Float)
    environmental_score = Column(Float)
    carbon_score = Column(Float)
    flood_risk = Column(Float)
    green_cover = Column(Float)
    water_usage = Column(Float)
    estimated_cost = Column(Float)
    happiness_score = Column(Float)
    budget_score = Column(Float)
    complexity_score = Column(Float)
    overall_score = Column(Float)
    
    status = Column(String, default="pending") # pending/completed/failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", backref="simulations")
    ai_responses = relationship("AIResponse", back_populates="simulation", cascade="all, delete")
    reports = relationship("Report", back_populates="simulation", cascade="all, delete")
