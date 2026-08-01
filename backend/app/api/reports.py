from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.simulation import Simulation
from app.models.report import Report
from app.schemas.report import ReportResponse
from app.services.report_service import generate_pdf_report

router = APIRouter()


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{simulation_id}/pdf")
async def generate_pdf(
    simulation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Simulation)
        .where(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id,
        )
        .options(
            selectinload(Simulation.ai_responses),
            selectinload(Simulation.project),
        )
    )
    simulation = result.scalar_one_or_none()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    pdf_path = await generate_pdf_report(db, simulation, current_user.id)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF generation failed")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"terravision_report_{simulation_id}.pdf",
    )
