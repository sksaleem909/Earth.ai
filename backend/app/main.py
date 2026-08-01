from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, dashboard, simulation, reports, analytics, chat
from app.core.database import engine, Base
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="TerraVision AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(simulation.router, prefix="/api/v1/simulations", tags=["simulations"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "Welcome to TerraVision AI API"}
