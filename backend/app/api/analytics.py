from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse

router = APIRouter()


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(current_user: User = Depends(get_current_user)):
    chart_data = {
        "project_distribution": [
            {"name": "Metro", "value": 15},
            {"name": "Flyover", "value": 8},
            {"name": "Hospital", "value": 12},
            {"name": "Residential", "value": 22},
            {"name": "Industrial Zone", "value": 10},
            {"name": "Solar Farm", "value": 18},
            {"name": "Urban Park", "value": 9},
            {"name": "Lake Restoration", "value": 6},
        ],
        "carbon_savings": [
            {"month": "Jan 2024", "value": 420},
            {"month": "Feb 2024", "value": 490},
            {"month": "Mar 2024", "value": 610},
            {"month": "Apr 2024", "value": 580},
            {"month": "May 2024", "value": 720},
            {"month": "Jun 2024", "value": 850},
            {"month": "Jul 2024", "value": 930},
            {"month": "Aug 2024", "value": 1050},
        ],
        "traffic_trends": [
            {"month": "Jan 2024", "before": 62, "after": 78},
            {"month": "Feb 2024", "before": 65, "after": 82},
            {"month": "Mar 2024", "before": 68, "after": 86},
            {"month": "Apr 2024", "before": 70, "after": 89},
            {"month": "May 2024", "before": 72, "after": 91},
            {"month": "Jun 2024", "before": 74, "after": 93},
        ],
        "simulation_timeline": [
            {"date": "2024-01", "count": 12},
            {"date": "2024-02", "count": 19},
            {"date": "2024-03", "count": 15},
            {"date": "2024-04", "count": 28},
            {"date": "2024-05", "count": 35},
            {"date": "2024-06", "count": 42},
            {"date": "2024-07", "count": 38},
            {"date": "2024-08", "count": 51},
        ],
        "score_distribution": [
            {"range": "0-20", "count": 2},
            {"range": "21-40", "count": 5},
            {"range": "41-60", "count": 14},
            {"range": "61-80", "count": 31},
            {"range": "81-100", "count": 18},
        ],
    }
    return AnalyticsResponse(chart_data=chart_data)
