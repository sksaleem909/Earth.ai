import os

base_dir = r"c:\Users\USER\Desktop\Earth.ai\backend"

files = {
    "app/api/__init__.py": "",
    "app/api/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import Token, UserResponse
from app.repositories.user_repo import get_user_by_email
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user
""",
    "app/api/dashboard.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.simulation import Simulation
from app.schemas.dashboard import DashboardStats

router = APIRouter()

@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Mock aggregation for dashboard
    result = await db.execute(select(func.count(Simulation.id)).where(Simulation.user_id == current_user.id))
    total_sims = result.scalar_one_or_none() or 0
    
    return {
        "total_simulations": total_sims,
        "projects_compared": total_sims,
        "avg_sustainability": 85.5 if total_sims > 0 else 0,
        "carbon_saved": 12500.5 * total_sims,
        "traffic_improvement": 22.4 if total_sims > 0 else 0,
        "recent_simulations": []
    }
""",
    "app/api/simulation.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.simulation import SimulationCreate, SimulationResponse
from app.services.simulation_engine import run_simulation
from app.models.simulation import Simulation

router = APIRouter()

@router.post("", response_model=SimulationResponse)
async def create_simulation(sim_data: SimulationCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        simulation = await run_simulation(db, sim_data.project, current_user.id)
        return simulation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[SimulationResponse])
async def list_simulations(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(
        select(Simulation)
        .where(Simulation.user_id == current_user.id)
        .options(selectinload(Simulation.ai_responses))
    )
    return result.scalars().all()

@router.get("/{sim_id}", response_model=SimulationResponse)
async def get_simulation(sim_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(
        select(Simulation)
        .where(Simulation.id == sim_id, Simulation.user_id == current_user.id)
        .options(selectinload(Simulation.ai_responses))
    )
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim
""",
    "app/api/reports.py": """from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.report import ReportResponse
from app.models.report import Report
from app.models.simulation import Simulation
from app.services.report_service import generate_pdf_report

router = APIRouter()

@router.get("", response_model=List[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Report).where(Report.user_id == current_user.id))
    return result.scalars().all()

@router.post("/{sim_id}/pdf")
async def create_pdf(sim_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Simulation).where(Simulation.id == sim_id, Simulation.user_id == current_user.id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
        
    pdf_path = await generate_pdf_report(db, sim, current_user.id)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"report_{sim_id}.pdf")
""",
    "app/api/analytics.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.analytics import AnalyticsResponse

router = APIRouter()

@router.get("", response_model=AnalyticsResponse)
async def get_analytics(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return {
        "chart_data": {
            "sustainability_trend": [80, 82, 85, 84, 88],
            "cost_distribution": {"residential": 40, "commercial": 30, "infrastructure": 30}
        }
    }
""",
    "app/api/chat.py": """from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
import google.generativeai as genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    simulation_id: int | None = None

class ChatResponse(BaseModel):
    response: str

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"User asks: {request.message}. Give a professional urban planning response.")
        return {"response": response.text}
    
    return {"response": f"I am the TerraVision AI assistant. Regarding your query '{request.message}', our analysis suggests focusing on mixed-use development to optimize traffic and sustainability."}
""",
    "app/repositories/__init__.py": "",
    "app/repositories/user_repo.py": """from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
""",
    "app/repositories/simulation_repo.py": "",
    "app/repositories/report_repo.py": "",
    "app/middleware/__init__.py": "",
    "app/middleware/audit_middleware.py": """from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Basic audit log simulation
        # Real implementation would use db session and get user from token
        response = await call_next(request)
        return response
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 3 created")
