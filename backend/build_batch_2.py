import os

base_dir = r"c:\Users\USER\Desktop\Earth.ai\backend"

files = {
    "app/models/__init__.py": """from .user import User
from .project import Project
from .simulation import Simulation
from .ai_response import AIResponse
from .report import Report
from .audit_log import AuditLog
""",
    "app/models/user.py": """from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user")
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "app/models/project.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
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
""",
    "app/models/simulation.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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
""",
    "app/models/ai_response.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
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
""",
    "app/models/report.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    executive_summary = Column(Text)
    pdf_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulation = relationship("Simulation", back_populates="reports")
""",
    "app/models/audit_log.py": """from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String)
    resource = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/schemas/__init__.py": "",
    "app/schemas/auth.py": """from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True
""",
    "app/schemas/dashboard.py": """from pydantic import BaseModel
from typing import List

class DashboardStats(BaseModel):
    total_simulations: int
    projects_compared: int
    avg_sustainability: float
    carbon_saved: float
    traffic_improvement: float
    recent_simulations: List[dict]
""",
    "app/schemas/simulation.py": """from pydantic import BaseModel
from typing import List, Optional

class ProjectCreate(BaseModel):
    name: str
    city: str
    latitude: float
    longitude: float
    project_type: str
    size_sqkm: float
    budget_million: float
    timeline_months: int
    boundary_geojson: str

class SimulationCreate(BaseModel):
    project: ProjectCreate

class AIResponseSchema(BaseModel):
    agent_type: str
    title: str
    analysis: str
    advantages: List[str]
    disadvantages: List[str]
    score: float
    recommendation: str
    
    class Config:
        from_attributes = True

class SimulationResponse(BaseModel):
    id: int
    project_id: int
    status: str
    traffic_score: Optional[float]
    environmental_score: Optional[float]
    carbon_score: Optional[float]
    flood_risk: Optional[float]
    green_cover: Optional[float]
    water_usage: Optional[float]
    estimated_cost: Optional[float]
    happiness_score: Optional[float]
    budget_score: Optional[float]
    complexity_score: Optional[float]
    overall_score: Optional[float]
    ai_responses: List[AIResponseSchema] = []
    
    class Config:
        from_attributes = True
""",
    "app/schemas/report.py": """from pydantic import BaseModel
from datetime import datetime

class ReportResponse(BaseModel):
    id: int
    simulation_id: int
    title: str
    pdf_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True
""",
    "app/schemas/analytics.py": """from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyticsResponse(BaseModel):
    chart_data: Dict[str, Any]
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 2 created")
