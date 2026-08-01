import asyncio
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
