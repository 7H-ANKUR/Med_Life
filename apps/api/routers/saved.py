from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List

from database import get_db
from models import SavedPlace, User
from schemas.saved import SavePlaceRequest, SavedPlaceOut
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


@router.get("", response_model=List[SavedPlaceOut])
async def list_saved(
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavedPlace)
        .where(SavedPlace.user_id == user.id)
        .order_by(SavedPlace.saved_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=SavedPlaceOut, status_code=201)
async def save_place(
    body: SavePlaceRequest,
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    # Check duplicate
    result = await db.execute(
        select(SavedPlace).where(
            SavedPlace.user_id == user.id,
            SavedPlace.google_place_id == body.google_place_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Place already saved")

    place = SavedPlace(user_id=user.id, **body.model_dump())
    db.add(place)
    await db.flush()
    return place


@router.delete("/{saved_id}", status_code=204)
async def delete_saved(
    saved_id: str,
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavedPlace).where(
            SavedPlace.id == saved_id,
            SavedPlace.user_id == user.id,
        )
    )
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Saved place not found")
    await db.delete(place)
