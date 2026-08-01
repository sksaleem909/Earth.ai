from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.simulation import Simulation
from app.models.report import Report


async def get_simulations_by_user(db: AsyncSession, user_id: int) -> list[Simulation]:
    result = await db.execute(
        select(Simulation)
        .where(Simulation.user_id == user_id)
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
        .order_by(Simulation.created_at.desc())
    )
    return list(result.scalars().all())


async def get_simulation_by_id(db: AsyncSession, sim_id: int) -> Simulation | None:
    result = await db.execute(
        select(Simulation)
        .where(Simulation.id == sim_id)
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
    )
    return result.scalar_one_or_none()


async def get_reports_by_user(db: AsyncSession, user_id: int) -> list[Report]:
    result = await db.execute(
        select(Report)
        .where(Report.user_id == user_id)
        .order_by(Report.created_at.desc())
    )
    return list(result.scalars().all())
