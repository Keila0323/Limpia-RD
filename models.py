from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host_id: Mapped[int] = mapped_column(Integer, index=True)
    location_city: Mapped[str] = mapped_column(String(100), index=True)
    location_neighborhood: Mapped[str] = mapped_column(String(120), index=True)
    location_country: Mapped[str] = mapped_column(String(120), default="Dominican Republic")
    property_type: Mapped[str] = mapped_column(String(80))
    service_type: Mapped[str] = mapped_column(String(80), index=True)
    scheduled_datetime: Mapped[datetime] = mapped_column(DateTime)
    budget: Mapped[float] = mapped_column(Numeric(10, 2))
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    payments: Mapped[list["Payment"]] = relationship(back_populates="service_request")
    reviews: Mapped[list["Review"]] = relationship(back_populates="service_request")


class Cleaner(Base):
    __tablename__ = "cleaners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), index=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    services_offered: Mapped[str] = mapped_column(Text)  # comma-separated
    cities_neighborhoods: Mapped[str] = mapped_column(Text)  # comma-separated
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    flat_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    languages: Mapped[str] = mapped_column(String(100), default="es")  # comma-separated
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    badges: Mapped[list["Badge"]] = relationship(
        back_populates="cleaner", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="cleaner", cascade="all, delete-orphan"
    )


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cleaner_id: Mapped[int] = mapped_column(ForeignKey("cleaners.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cleaner: Mapped["Cleaner"] = relationship(back_populates="badges")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cleaner_id: Mapped[int] = mapped_column(ForeignKey("cleaners.id", ondelete="CASCADE"))
    host_id: Mapped[int] = mapped_column(Integer, index=True)
    service_request_id: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE")
    )
    rating: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(2), default="es")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    cleaner: Mapped["Cleaner"] = relationship(back_populates="reviews")
    service_request: Mapped["ServiceRequest"] = relationship(back_populates="reviews")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_request_id: Mapped[int] = mapped_column(ForeignKey("service_requests.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    provider: Mapped[str] = mapped_column(String(30), default="stripe")
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    status: Mapped[str] = mapped_column(String(20), default="created", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    service_request: Mapped["ServiceRequest"] = relationship(back_populates="payments")
