from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SavePlaceRequest(BaseModel):
    google_place_id: str
    place_name: Optional[str] = None
    place_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    rating: Optional[float] = None
    specialist_type: Optional[str] = None
    notes: Optional[str] = None


class SavedPlaceOut(BaseModel):
    id: str
    google_place_id: str
    place_name: Optional[str]
    place_type: Optional[str]
    city: Optional[str]
    rating: Optional[float]
    specialist_type: Optional[str]
    notes: Optional[str]
    saved_at: datetime

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    google_place_id: str
    search_id: Optional[str] = None
    rating: int  # 1 or -1
    comment: Optional[str] = None
    visited: bool = False


class SearchHistoryOut(BaseModel):
    id: str
    symptom_text: str
    specialist_type: Optional[str]
    urgency_level: Optional[str]
    city: Optional[str]
    result_count: Optional[int]
    emergency_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True
