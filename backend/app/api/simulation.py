from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.simulation import Simulation
from app.models.project import Project
from app.schemas.simulation import SimulationCreate, SimulationResponse
from app.services.simulation_engine import run_simulation

router = APIRouter()


@router.post("/", response_model=SimulationResponse)
async def create_simulation(
    sim_in: SimulationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    simulation = await run_simulation(db, sim_in.project, current_user.id)
    # Re-fetch with all relationships loaded
    result = await db.execute(
        select(Simulation)
        .where(Simulation.id == simulation.id)
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
    )
    return result.scalar_one()


@router.get("/", response_model=List[SimulationResponse])
async def list_simulations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Simulation)
        .where(Simulation.user_id == current_user.id)
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
        .order_by(Simulation.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{sim_id}", response_model=SimulationResponse)
async def get_simulation(
    sim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Simulation)
        .where(Simulation.id == sim_id, Simulation.user_id == current_user.id)
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
    )
    simulation = result.scalar_one_or_none()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation
