from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


MOCK_RESPONSES = {
    "metro": "Based on TerraVision AI analysis, metro systems in dense urban corridors typically yield a 35% reduction in surface traffic and cut per-capita carbon emissions by 22%. Key success factors include feeder bus integration and last-mile connectivity planning.",
    "flyover": "Flyovers offer short-term traffic relief but carry long-term downsides: they sever communities, increase noise pollution, and rarely solve root congestion. Our simulations show BRT alternatives often score 15-20 points higher on sustainability metrics.",
    "hospital": "Hospital placement simulations should prioritize catchment area analysis, emergency vehicle access times, and proximity to residential zones. A well-placed 500-bed facility can serve 400,000 residents while reducing average emergency response times by 40%.",
    "solar": "Solar farm simulations in our system account for land use efficiency, grid connectivity costs, and shadow impact on adjacent zones. A 10 sq km solar installation typically offsets 85,000 tons of CO2 annually.",
    "park": "Urban parks consistently score highest on citizen happiness metrics (avg 88/100) in our simulations. Green cover above 30% correlates with a 12% reduction in urban heat island effect and significant mental health benefits.",
    "residential": "Residential development simulations balance density, transit access, and green space. Mixed-income developments within 500m of transit nodes score 18% higher on overall sustainability than car-dependent suburbs.",
    "traffic": "Traffic improvement strategies in TerraVision AI consider peak hour flow, modal shift potential, and intersection capacity. Signal optimization alone can yield 8-12% throughput improvements without new infrastructure.",
    "carbon": "Carbon reduction potential varies by project type: solar farms (-85k tons/yr), urban parks (-12k tons/yr), metro extensions (-45k tons/yr). Our AI weights long-term carbon trajectories over 30-year horizons.",
    "flood": "Flood risk assessment in our platform integrates topographic data, rainfall patterns, and drainage capacity. Projects in low-lying zones below elevation 5m require mandatory green infrastructure buffers.",
    "budget": "Budget optimization in urban projects follows an 80/20 principle — 80% of sustainability gains come from 20% of interventions. Our Economic AI agent identifies high-ROI quick wins within your budget envelope.",
}


def get_mock_response(message: str) -> str:
    msg_lower = message.lower()
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in msg_lower:
            return response
    return (
        f"Based on TerraVision AI's urban intelligence models, your query about '{message}' "
        "involves multiple planning dimensions. I recommend running a full simulation with "
        "your specific parameters — this will generate Environmental, Economic, Traffic, "
        "and Citizen impact scores, plus an executive recommendation from our Chief Planner AI. "
        "Would you like to start a new scenario in the Scenario Builder?"
    )


@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(
                f"You are an expert urban planning AI assistant for TerraVision AI platform. "
                f"Answer this query concisely and professionally: {request.message}"
            )
            return {"response": response.text, "context": {"provider": "gemini"}}
        except Exception:
            pass

    return {
        "response": get_mock_response(request.message),
        "context": {"provider": "mock"},
    }
