import os
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
