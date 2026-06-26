from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database import get_db
from models import FeeEstimate
from services.fee_service import get_fee_range

router = APIRouter()


@router.get("/fees")
async def get_fees(
    specialist_type: str = Query(...),
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    fee_data = await get_fee_range(specialist_type, city, db)
    return {
        "specialist_type": specialist_type,
        "city": city,
        **fee_data,
    }
