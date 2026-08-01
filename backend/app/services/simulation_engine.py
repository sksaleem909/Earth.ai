from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.simulation import Simulation
from app.services.ai_decision_engine import generate_ai_responses
import random

# Score profiles for each project type
PROJECT_PROFILES = {
    "metro": {
        "traffic": 88, "env": 72, "carbon": 85, "flood": 20,
        "green": 45, "water": 35, "happiness": 86, "budget": 62, "complexity": 78,
    },
    "flyover": {
        "traffic": 75, "env": 45, "carbon": 50, "flood": 30,
        "green": 25, "water": 25, "happiness": 55, "budget": 70, "complexity": 65,
    },
    "hospital": {
        "traffic": 60, "env": 70, "carbon": 65, "flood": 25,
        "green": 55, "water": 60, "happiness": 92, "budget": 55, "complexity": 72,
    },
    "residential area": {
        "traffic": 65, "env": 75, "carbon": 70, "flood": 35,
        "green": 65, "water": 55, "happiness": 80, "budget": 72, "complexity": 55,
    },
    "industrial zone": {
        "traffic": 50, "env": 35, "carbon": 30, "flood": 40,
        "green": 20, "water": 70, "happiness": 40, "budget": 85, "complexity": 70,
    },
    "solar farm": {
        "traffic": 90, "env": 95, "carbon": 98, "flood": 15,
        "green": 70, "water": 15, "happiness": 82, "budget": 68, "complexity": 45,
    },
    "urban park": {
        "traffic": 85, "env": 95, "carbon": 90, "flood": 10,
        "green": 95, "water": 30, "happiness": 95, "budget": 80, "complexity": 35,
    },
    "lake restoration": {
        "traffic": 80, "env": 98, "carbon": 88, "flood": 8,
        "green": 90, "water": 20, "happiness": 90, "budget": 75, "complexity": 50,
    },
    "ev charging network": {
        "traffic": 82, "env": 85, "carbon": 90, "flood": 15,
        "green": 50, "water": 20, "happiness": 85, "budget": 65, "complexity": 55,
    },
    "road expansion": {
        "traffic": 70, "env": 40, "carbon": 38, "flood": 45,
        "green": 30, "water": 30, "happiness": 62, "budget": 60, "complexity": 60,
    },
}

DEFAULT_PROFILE = {
    "traffic": 65, "env": 65, "carbon": 65, "flood": 30,
    "green": 55, "water": 45, "happiness": 70, "budget": 65, "complexity": 60,
}


def _jitter(base: float, lo: float = -8.0, hi: float = 8.0) -> float:
    return min(100.0, max(0.0, base + random.uniform(lo, hi)))


async def run_simulation(db: AsyncSession, project_data, user_id: int) -> Simulation:
    # 1. Persist project
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
        boundary_geojson=project_data.boundary_geojson,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 2. Lookup score profile
    pt_key = project.project_type.lower()
    profile = PROJECT_PROFILES.get(pt_key, DEFAULT_PROFILE)

    # 3. Modifiers based on size and budget
    size_factor = min(1.3, max(0.7, project.size_sqkm / 10.0))
    budget_ratio = project.budget_million / max(1.0, project.size_sqkm * 80)
    budget_factor = min(1.3, max(0.7, budget_ratio))
    timeline_factor = min(1.1, max(0.9, project.timeline_months / 36.0))

    traffic_score = _jitter(profile["traffic"] * (2 - size_factor))
    environmental_score = _jitter(profile["env"] * budget_factor)
    carbon_score = _jitter(profile["carbon"] * budget_factor)
    flood_risk = _jitter(profile["flood"] * size_factor, -5, 5)
    green_cover = _jitter(profile["green"] * budget_factor)
    water_usage = _jitter(profile["water"] * size_factor, -5, 5)
    estimated_cost = project.budget_million * (1 + random.uniform(0.05, 0.25))
    happiness_score = _jitter(profile["happiness"])
    budget_score = _jitter(
        min(100, profile["budget"] * timeline_factor / max(0.5, budget_ratio))
    )
    complexity_score = _jitter(profile["complexity"] * size_factor)

    overall_score = (
        traffic_score * 0.20
        + environmental_score * 0.20
        + carbon_score * 0.15
        + happiness_score * 0.20
        + budget_score * 0.15
        + (100 - flood_risk) * 0.10
    )

    sim = Simulation(
        project_id=project.id,
        user_id=user_id,
        traffic_score=round(traffic_score, 1),
        environmental_score=round(environmental_score, 1),
        carbon_score=round(carbon_score, 1),
        flood_risk=round(flood_risk, 1),
        green_cover=round(green_cover, 1),
        water_usage=round(water_usage, 1),
        estimated_cost=round(estimated_cost, 2),
        happiness_score=round(happiness_score, 1),
        budget_score=round(budget_score, 1),
        complexity_score=round(complexity_score, 1),
        overall_score=round(overall_score, 1),
        status="completed",
    )
    db.add(sim)
    await db.commit()
    await db.refresh(sim)

    # 4. Generate AI expert responses
    await generate_ai_responses(db, sim.id)
    await db.refresh(sim)
    return sim
