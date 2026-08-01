from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    project_type = Column(String) # residential, commercial, infrastructure, mixed
    size_sqkm = Column(Float)
    budget_million = Column(Float)
    timeline_months = Column(Integer)
    boundary_geojson = Column(String) # Stored as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
