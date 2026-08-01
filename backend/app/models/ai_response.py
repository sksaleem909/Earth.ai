from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    agent_type = Column(String, nullable=False)
    title = Column(String)
    analysis = Column(Text)
    advantages = Column(JSON)
    disadvantages = Column(JSON)
    score = Column(Float)
    recommendation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulation = relationship("Simulation", back_populates="ai_responses")
