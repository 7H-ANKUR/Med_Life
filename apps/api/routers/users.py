from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from database import get_db
from models import User
from routers.auth import get_current_user

router = APIRouter()

async def _get_user_from_header(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.split(" ")[1]
    return await get_current_user(token, db)

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    default_city: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    default_city: Optional[str] = None
    language_pref: str

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(_get_user_from_header)):
    return current_user

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    body: UserProfileUpdate,
    current_user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db)
):
    if body.display_name is not None:
        current_user.display_name = body.display_name
    if body.email is not None:
        # Check if email is already taken by someone else
        result = await db.execute(select(User).where(User.email == body.email))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = body.email
    if body.phone_number is not None:
        current_user.phone_number = body.phone_number
    if body.default_city is not None:
        current_user.default_city = body.default_city

    await db.flush()
    return current_user
