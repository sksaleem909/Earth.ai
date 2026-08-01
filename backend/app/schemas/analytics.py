from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyticsResponse(BaseModel):
    chart_data: Dict[str, Any]
