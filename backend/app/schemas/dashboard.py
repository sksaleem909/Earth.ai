from pydantic import BaseModel
from typing import List

class DashboardStats(BaseModel):
    total_simulations: int
    projects_compared: int
    avg_sustainability: float
    carbon_saved: float
    traffic_improvement: float
    recent_simulations: List[dict]
