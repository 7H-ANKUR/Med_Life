from pydantic import BaseModel, field_validator
from typing import Optional


class SymptomRequest(BaseModel):
    symptom_text: str
    city: Optional[str] = None
    language: Optional[str] = "en"

    @field_validator("symptom_text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("symptom_text cannot be empty")
        if len(v) > 500:
            raise ValueError("symptom_text too long (max 500 chars)")
        return v


class FeeEstimateOut(BaseModel):
    min: int
    max: int
    currency: str = "INR"
    note: str = "Estimate only. Actual fees may vary."


class AnalysisResult(BaseModel):
    specialist_type: str
    specialist_explanation: str
    urgency_level: str         # low | moderate | high | emergency
    urgency_reason: str
    emergency_mode: bool
    fee_estimate: Optional[FeeEstimateOut] = None
    search_id: Optional[str] = None
    fallback: bool = False
