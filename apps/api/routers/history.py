from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List

from database import get_db
from models import Search, User
from schemas.saved import SearchHistoryOut
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


@router.get("", response_model=List[SearchHistoryOut])
async def get_history(
    limit: int = Query(10, ge=1, le=25),
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Search)
        .where(Search.user_id == user.id)
        .order_by(Search.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{search_id}", status_code=204)
async def delete_history_item(
    search_id: str,
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Search).where(Search.id == search_id, Search.user_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "History item not found")
    await db.delete(item)


@router.delete("", status_code=204)
async def clear_all_history(
    user: User = Depends(_get_user_from_header),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(delete(Search).where(Search.user_id == user.id))
