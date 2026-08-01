from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    city: str
    latitude: float
    longitude: float
    project_type: str
    size_sqkm: float
    budget_million: float
    timeline_months: int
    boundary_geojson: str = "{}"


class SimulationCreate(BaseModel):
    project: ProjectCreate


class ProjectResponse(BaseModel):
    id: int
    name: str
    city: str
    project_type: str
    size_sqkm: float
    budget_million: float
    timeline_months: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class AIResponseSchema(BaseModel):
    id: int
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
    traffic_score: Optional[float] = None
    environmental_score: Optional[float] = None
    carbon_score: Optional[float] = None
    flood_risk: Optional[float] = None
    green_cover: Optional[float] = None
    water_usage: Optional[float] = None
    estimated_cost: Optional[float] = None
    happiness_score: Optional[float] = None
    budget_score: Optional[float] = None
    complexity_score: Optional[float] = None
    overall_score: Optional[float] = None
    created_at: Optional[datetime] = None
    project: Optional[ProjectResponse] = None
    ai_responses: List[AIResponseSchema] = []

    class Config:
        from_attributes = True


class SimulationListItem(BaseModel):
    id: int
    project_id: int
    overall_score: Optional[float] = None
    status: str
    created_at: Optional[datetime] = None
    project: Optional[ProjectResponse] = None

    class Config:
        from_attributes = True
