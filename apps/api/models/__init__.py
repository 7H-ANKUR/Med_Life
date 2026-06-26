import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, Float, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base


def new_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    default_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language_pref: Mapped[str] = mapped_column(String(20), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    searches: Mapped[list["Search"]] = relationship("Search", back_populates="user")
    saved_places: Mapped[list["SavedPlace"]] = relationship("SavedPlace", back_populates="user")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")


class Search(Base):
    __tablename__ = "searches"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    symptom_text: Mapped[str] = mapped_column(Text, nullable=False)
    specialist_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    urgency_level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low|moderate|high|emergency
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    fee_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fee_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emergency_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user: Mapped["User | None"] = relationship("User", back_populates="searches")


class SavedPlace(Base):
    __tablename__ = "saved_places"
    __table_args__ = (UniqueConstraint("user_id", "doctor_id", name="uq_user_doctor"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    place_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    place_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # hospital|clinic|pharmacy
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    specialist_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="saved_places")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="saved_by")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    doctor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    search_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("searches.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1=thumbs_up, -1=thumbs_down
    comment: Mapped[str | None] = mapped_column(String(200), nullable=True)
    visited: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User | None"] = relationship("User", back_populates="feedbacks")
    doctor: Mapped["Doctor | None"] = relationship("Doctor", back_populates="feedbacks")

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    degree: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dp_score: Mapped[str | None] = mapped_column(String(50), nullable=True)
    npv_value: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    consult_fee: Mapped[str | None] = mapped_column(String(50), nullable=True)
    years_of_experience: Mapped[str | None] = mapped_column(String(50), nullable=True)
    speciality: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    saved_by: Mapped[list["SavedPlace"]] = relationship("SavedPlace", back_populates="doctor")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="doctor")


class FeeEstimate(Base):
    __tablename__ = "fee_estimates"
    __table_args__ = (UniqueConstraint("city", "specialist_type", name="uq_city_specialist"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specialist_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    fee_min: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_max: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class CityConfig(Base):
    __tablename__ = "city_configs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    city_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    country_code: Mapped[str] = mapped_column(String(2), default="IN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    search_radius: Mapped[int] = mapped_column(Integer, default=5000)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    symptom_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(50), nullable=True)  # called_112|navigated_er|dismissed
    nearest_er_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
