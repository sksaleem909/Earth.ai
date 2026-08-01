import os

base_dir = r"c:\Users\USER\Desktop\Earth.ai\backend"

files = {
    "app/services/__init__.py": "",
    "app/services/simulation_engine.py": """from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.simulation import Simulation
from app.services.ai_decision_engine import generate_ai_responses
import random

async def run_simulation(db: AsyncSession, project_data: dict, user_id: int) -> Simulation:
    # 1. Create Project
    project = Project(
        user_id=user_id,
        name=project_data.name,
        city=project_data.city,
        latitude=project_data.latitude,
        longitude=project_data.longitude,
        project_type=project_data.project_type,
        size_sqkm=project_data.size_sqkm,
        budget_million=project_data.budget_million,
        timeline_months=project_data.timeline_months,
        boundary_geojson=project_data.boundary_geojson
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 2. Calculate scores based on project_type
    pt = project.project_type.lower()
    
    # Base multipliers
    if pt == 'residential':
        traffic_base = 70
        env_base = 80
        cost_base = 60
    elif pt == 'commercial':
        traffic_base = 50
        env_base = 65
        cost_base = 85
    elif pt == 'infrastructure':
        traffic_base = 85
        env_base = 50
        cost_base = 90
    else: # mixed
        traffic_base = 65
        env_base = 75
        cost_base = 75
        
    # Variation based on size and budget
    size_factor = min(1.5, max(0.5, project.size_sqkm / 10.0))
    budget_factor = min(1.5, max(0.5, project.budget_million / (project.size_sqkm * 100)))

    sim = Simulation(
        project_id=project.id,
        user_id=user_id,
        traffic_score=min(100, max(0, traffic_base * (2 - size_factor) + random.uniform(-5, 5))),
        environmental_score=min(100, max(0, env_base * budget_factor + random.uniform(-5, 5))),
        carbon_score=min(100, max(0, env_base * 0.9 + random.uniform(-5, 5))),
        flood_risk=min(100, max(0, 30 * size_factor + random.uniform(-5, 5))),
        green_cover=min(100, max(0, env_base * 0.8 * budget_factor + random.uniform(-5, 5))),
        water_usage=min(100, max(0, 60 * size_factor + random.uniform(-5, 5))),
        estimated_cost=project.budget_million * (1 + random.uniform(0.05, 0.2)),
        happiness_score=min(100, max(0, 75 + random.uniform(-10, 10))),
        budget_score=min(100, max(0, 100 - (budget_factor * 10) + random.uniform(-5, 5))),
        complexity_score=min(100, max(0, 50 * size_factor + random.uniform(-5, 5))),
        status="completed"
    )
    
    sim.overall_score = (sim.traffic_score + sim.environmental_score + sim.happiness_score + sim.budget_score) / 4
    
    db.add(sim)
    await db.commit()
    await db.refresh(sim)

    # 3. Generate AI Responses
    await generate_ai_responses(db, sim.id)
    
    await db.refresh(sim)
    return sim
""",
    "app/services/ai_decision_engine.py": """from sqlalchemy.ext.asyncio import AsyncSession
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
""",
    "app/services/report_service.py": """import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.simulation import Simulation
from app.models.report import Report

async def generate_pdf_report(db: AsyncSession, sim: Simulation, user_id: int) -> str:
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    pdf_path = os.path.join(reports_dir, f"report_{sim.id}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, f"TerraVision AI - Simulation Report #{sim.id}")
    c.drawString(100, 730, f"Overall Score: {sim.overall_score:.2f}")
    c.drawString(100, 710, f"Traffic Score: {sim.traffic_score:.2f}")
    c.drawString(100, 690, f"Environmental Score: {sim.environmental_score:.2f}")
    c.drawString(100, 670, f"Budget Score: {sim.budget_score:.2f}")
    c.save()

    report = Report(
        simulation_id=sim.id,
        user_id=user_id,
        title=f"Report for Sim {sim.id}",
        executive_summary=f"Summary of simulation {sim.id} with overall score {sim.overall_score:.2f}",
        pdf_path=pdf_path
    )
    db.add(report)
    await db.commit()
    
    return pdf_path
""",
    "app/utils/__init__.py": "",
    "seed.py": """import asyncio
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.project import Project
from app.models.simulation import Simulation
from app.services.ai_decision_engine import generate_ai_responses

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create admin user
        admin = User(
            email="admin@terravision.ai",
            password_hash=get_password_hash("Password123"),
            full_name="Admin User",
            role="admin"
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        # Create sample project
        proj = Project(
            user_id=admin.id,
            name="Downtown Revitalization",
            city="Metropolis",
            latitude=40.7128,
            longitude=-74.0060,
            project_type="mixed",
            size_sqkm=5.5,
            budget_million=250.0,
            timeline_months=36,
            boundary_geojson="{}"
        )
        db.add(proj)
        await db.commit()
        await db.refresh(proj)

        # Create sample simulation
        sim = Simulation(
            project_id=proj.id,
            user_id=admin.id,
            traffic_score=75.5,
            environmental_score=82.0,
            carbon_score=80.0,
            flood_risk=20.0,
            green_cover=35.0,
            water_usage=45.0,
            estimated_cost=260.0,
            happiness_score=88.0,
            budget_score=70.0,
            complexity_score=85.0,
            overall_score=79.5,
            status="completed"
        )
        db.add(sim)
        await db.commit()
        await db.refresh(sim)

        # Generate AI Responses
        await generate_ai_responses(db, sim.id)
        
        print("Database seeded successfully with admin user and sample data!")

if __name__ == "__main__":
    asyncio.run(seed_data())
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 4 created")
