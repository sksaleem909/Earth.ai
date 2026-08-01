from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String)
    resource = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
