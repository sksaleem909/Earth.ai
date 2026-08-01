from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportResponse(BaseModel):
    id: int
    simulation_id: int
    title: str
    executive_summary: Optional[str] = None
    pdf_path: str
    created_at: datetime

    class Config:
        from_attributes = True
