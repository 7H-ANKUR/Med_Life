"""
Fee estimation service.
Queries fee_estimates table → national fallback if not found.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import FeeEstimate


# ─── National Fallback Fee Table ──────────────────────────
# Derived from docter.csv analysis (P25–P75 national medians)
NATIONAL_FALLBACK = {
    "General Physician":   (300,  800),
    "Cardiologist":        (800, 2500),
    "Dermatologist":       (500, 1500),
    "Orthopedic Surgeon":  (600, 2000),
    "Gynecologist":        (500, 1500),
    "Pediatrician":        (400, 1000),
    "Neurologist":         (800, 2500),
    "Gastroenterologist":  (600, 1800),
    "ENT Specialist":      (400, 1200),
    "Ophthalmologist":     (500, 1500),
    "Dentist":             (300, 1500),
    "Nephrologist":        (800, 2000),
    "Psychiatrist":        (800, 2000),
    "Physiotherapist":     (400, 1000),
    "Endocrinologist":     (600, 1800),
    "Urologist":           (600, 1800),
    "Emergency Physician": (500, 2000),
}

DEFAULT_RANGE = (300, 1500)


async def get_fee_range(
    specialist_type: str,
    city: str | None,
    db: AsyncSession
) -> dict:
    """
    Get fee range for specialist × city.
    Priority: DB (city-specific) → DB (any city) → national fallback.
    """
    # 1. Try city-specific from DB
    if city:
        stmt = select(FeeEstimate).where(
            FeeEstimate.specialist_type == specialist_type,
            FeeEstimate.city == city,
            FeeEstimate.is_active == True,
        )
        result = await db.execute(stmt)
        fee = result.scalar_one_or_none()
        if fee:
            return {
                "min": fee.fee_min,
                "max": fee.fee_max,
                "currency": "INR",
                "note": "Estimate only. Actual fees may vary.",
                "data_source": fee.data_source,
            }

    # 2. National fallback from hardcoded table
    lo, hi = NATIONAL_FALLBACK.get(specialist_type, DEFAULT_RANGE)
    return {
        "min": lo,
        "max": hi,
        "currency": "INR",
        "note": "Estimate only. Actual fees may vary.",
        "data_source": "national_median",
    }
