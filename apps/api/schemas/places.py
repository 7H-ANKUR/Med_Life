from pydantic import BaseModel
from typing import Optional, List


class LocationPoint(BaseModel):
    lat: float
    lng: float


class FeeRange(BaseModel):
    min: int
    max: int
    currency: str = "INR"


class PlaceResult(BaseModel):
    place_id: str
    name: str
    place_type: str
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    open_now: bool = False
    distance_meters: Optional[int] = None
    distance_label: Optional[str] = None
    fee_estimate: Optional[FeeRange] = None
    specialist_types: List[str] = []
    score: Optional[float] = None
    emergency_capable: bool = False
    location: Optional[LocationPoint] = None
    maps_url: Optional[str] = None
    photo_url: Optional[str] = None
    speciality: Optional[str] = None


class NearbyRequest(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = None
    specialist_type: Optional[str] = None
    place_type: Optional[str] = "all"  # hospital|clinic|pharmacy|all
    emergency: bool = False
    open_now: Optional[bool] = None
    budget_max: Optional[int] = None
    radius: int = 5000
    rating_min: Optional[float] = None
    language: Optional[str] = None
    limit: int = 10
    search_id: Optional[str] = None


class NearbyResponse(BaseModel):
    results: List[PlaceResult]
    total: int
    radius_used: int
    emergency_mode: bool
    city: Optional[str] = None


class RouteResponse(BaseModel):
    distance_meters: Optional[int] = None
    duration_seconds: Optional[int] = None
    duration_label: Optional[str] = None
    maps_deeplink: str
