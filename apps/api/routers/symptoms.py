from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from schemas.symptoms import SymptomRequest, AnalysisResult, FeeEstimateOut
from services.ai_service import analyze_symptoms
from services.fee_service import get_fee_range
from models import Search
from config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/analyze-symptoms", response_model=AnalysisResult)
@limiter.limit(settings.rate_limit_ai)
async def analyze(
    request: Request,
    body: SymptomRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. Call AI
    ai_result = await analyze_symptoms(body.symptom_text, body.city)

    # 2. Get fee estimate
    specialist_type = ai_result.get("specialist_type", "General Physician")
    fee_data = await get_fee_range(specialist_type, body.city, db)
    fee_out = FeeEstimateOut(**fee_data) if fee_data else None

    # 3. Save search record
    search = Search(
        symptom_text=body.symptom_text,
        specialist_type=specialist_type,
        urgency_level=ai_result.get("urgency_level"),
        city=body.city,
        emergency_mode=ai_result.get("emergency_mode", False),
        fee_min=fee_data.get("min") if fee_data else None,
        fee_max=fee_data.get("max") if fee_data else None,
    )
    db.add(search)
    await db.flush()

    return AnalysisResult(
        specialist_type=specialist_type,
        specialist_explanation=ai_result.get("specialist_explanation", ""),
        urgency_level=ai_result.get("urgency_level", "moderate"),
        urgency_reason=ai_result.get("urgency_reason", ""),
        emergency_mode=ai_result.get("emergency_mode", False),
        fee_estimate=fee_out,
        search_id=search.id,
        fallback=ai_result.get("fallback", False),
    )
