from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.simulation import Simulation
from app.models.ai_response import AIResponse
from app.core.config import settings
import google.generativeai as genai
import json

async def generate_ai_responses(db: AsyncSession, simulation_id: int):
    result = await db.execute(
        select(Simulation).where(Simulation.id == simulation_id).options(selectinload(Simulation.project))
    )
    sim = result.scalar_one_or_none()
    if not sim:
        return

    agents = [
        {"type": "Environmental Expert", "role": "sustainability and ecological impact"},
        {"type": "Economist", "role": "budget, economic feasibility, and long-term ROI"},
        {"type": "Traffic Expert", "role": "mobility, congestion, and transport infrastructure"},
        {"type": "Citizen Representative", "role": "community well-being, noise, and livability"},
        {"type": "Chief Planner", "role": "synthesizing all views into a final decision"}
    ]

    use_gemini = False
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            use_gemini = True
        except Exception:
            pass

    for agent in agents:
        if use_gemini:
            prompt = f"Act as a {agent['type']} focusing on {agent['role']}. Analyze a {sim.project.project_type} project in {sim.project.city} sized {sim.project.size_sqkm} sqkm with budget ${sim.project.budget_million}M. Overall score: {sim.overall_score}. Provide JSON with: title, analysis (text), advantages (list), disadvantages (list), score (0-100), recommendation (text)."
            try:
                response = model.generate_content(prompt)
                # Extremely naive JSON extraction, assumes model returns clean JSON
                data = json.loads(response.text.replace('```json', '').replace('```', ''))
            except Exception:
                data = get_mock_data(agent['type'], sim)
        else:
            data = get_mock_data(agent['type'], sim)

        ai_resp = AIResponse(
            simulation_id=simulation_id,
            agent_type=agent['type'],
            title=data['title'],
            analysis=data['analysis'],
            advantages=data['advantages'],
            disadvantages=data['disadvantages'],
            score=data['score'],
            recommendation=data['recommendation']
        )
        db.add(ai_resp)

    await db.commit()

def get_mock_data(agent_type: str, sim: Simulation) -> dict:
    pt = sim.project.project_type
    if agent_type == "Environmental Expert":
        return {
            "title": "Ecological Impact Analysis",
            "analysis": f"The {pt} project shows an environmental score of {sim.environmental_score:.1f}. Green cover is at {sim.green_cover:.1f}%, which is adequate but could be improved with vertical gardens.",
            "advantages": ["Promotes local biodiversity", "Adequate green spacing planned"],
            "disadvantages": ["Water usage is relatively high", "Potential habitat disruption during construction"],
            "score": sim.environmental_score,
            "recommendation": "Incorporate rainwater harvesting and expand the green corridors."
        }
    elif agent_type == "Economist":
        return {
            "title": "Financial Feasibility Review",
            "analysis": f"With a budget of ${sim.project.budget_million}M, the estimated cost is ${sim.estimated_cost:.1f}M. The budget score is {sim.budget_score:.1f}.",
            "advantages": ["High potential for property value appreciation", "Strong job creation during construction"],
            "disadvantages": ["Risk of cost overruns", "High upfront infrastructure costs"],
            "score": sim.budget_score,
            "recommendation": "Implement strict cost controls and consider public-private partnerships."
        }
    elif agent_type == "Traffic Expert":
        return {
            "title": "Mobility and Transport Impact",
            "analysis": f"Traffic score is {sim.traffic_score:.1f}. The {pt} density will impact local road networks significantly.",
            "advantages": ["Proximity to main transit hubs", "Includes pedestrian-friendly zones"],
            "disadvantages": ["Increased peak hour congestion", "Insufficient parking allocations"],
            "score": sim.traffic_score,
            "recommendation": "Add dedicated bus lanes and expand bicycle networks."
        }
    elif agent_type == "Citizen Representative":
        return {
            "title": "Community Well-being Assessment",
            "analysis": f"Happiness score is projected at {sim.happiness_score:.1f}. The community values the {pt} development but has concerns.",
            "advantages": ["New community facilities", "Modernized public spaces"],
            "disadvantages": ["Construction noise and disruption", "Gentrification risks"],
            "score": sim.happiness_score,
            "recommendation": "Establish a community feedback committee during construction."
        }
    else: # Chief Planner
        return {
            "title": "Executive Planning Summary",
            "analysis": f"Overall project score stands at {sim.overall_score:.1f}. Balancing economic gains with environmental and social factors is crucial for this {pt} development.",
            "advantages": ["Comprehensive development plan", "Strong overall viability"],
            "disadvantages": ["Complex stakeholder management", "Multi-year construction fatigue"],
            "score": sim.overall_score,
            "recommendation": "Proceed with caution, incorporating the recommendations from the environmental and traffic committees."
        }
