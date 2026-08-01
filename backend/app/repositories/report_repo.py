from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.report import Report


async def get_reports_by_user(db: AsyncSession, user_id: int) -> list[Report]:
    result = await db.execute(
        select(Report)
        .where(Report.user_id == user_id)
        .order_by(Report.created_at.desc())
    )
    return list(result.scalars().all())
