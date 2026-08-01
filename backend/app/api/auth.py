from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import UserLogin, UserResponse
from app.repositories.user_repo import get_user_by_email
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(subject=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
        },
    }
