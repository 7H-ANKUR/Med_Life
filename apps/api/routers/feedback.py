from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from models import Feedback, User
from schemas.saved import FeedbackRequest
from routers.auth import get_current_user

router = APIRouter()


async def _get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        return await get_current_user(token, db)
    except Exception:
        return None


@router.post("/feedback", status_code=201)
async def submit_feedback(
    body: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(_get_optional_user),
):
    if body.rating not in (1, -1):
        raise HTTPException(400, "rating must be 1 (thumbs up) or -1 (thumbs down)")
    if body.comment and len(body.comment) > 200:
        raise HTTPException(400, "comment must be <= 200 characters")

    fb = Feedback(
        user_id=user.id if user else None,
        google_place_id=body.google_place_id,
        search_id=body.search_id,
        rating=body.rating,
        comment=body.comment,
        visited=body.visited,
    )
    db.add(fb)
    await db.flush()
    return {"id": fb.id}
