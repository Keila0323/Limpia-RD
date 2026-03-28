from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CleanerBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    bio: str | None = None
    services_offered: list[str] = Field(min_length=1)
    cities_neighborhoods: list[str] = Field(min_length=1)
    hourly_rate: Decimal | None = Field(default=None, ge=0)
    flat_rate: Decimal | None = Field(default=None, ge=0)
    years_experience: int = Field(default=0, ge=0)
    languages: list[Literal["en", "es"]] = Field(default_factory=lambda: ["es"])


class CleanerCreate(CleanerBase):
    pass


class CleanerRead(CleanerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime


class BadgeBase(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    description: str | None = None
    image_url: str = Field(min_length=5, max_length=500)


class BadgeCreate(BadgeBase):
    pass


class BadgeRead(BadgeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cleaner_id: int
    created_at: datetime


class CleanerDetail(CleanerRead):
    badges: list[BadgeRead] = []


class ServiceRequestBase(BaseModel):
    host_id: int
    location_city: str
    location_neighborhood: str
    location_country: str = "Dominican Republic"
    property_type: str
    service_type: str
    scheduled_datetime: datetime
    budget: Decimal = Field(ge=0)
    special_instructions: str | None = None
    status: Literal["pending", "confirmed", "paid", "completed", "cancelled"] = "pending"

    @field_validator("scheduled_datetime")
    @classmethod
    def must_be_future(cls, value: datetime) -> datetime:
        if value <= datetime.utcnow():
            raise ValueError("scheduled_datetime must be in the future")
        return value


class ServiceRequestCreate(ServiceRequestBase):
    pass


class ServiceRequestRead(ServiceRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ReviewBase(BaseModel):
    host_id: int
    service_request_id: int
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=200)
    comment: str | None = None
    language: Literal["en", "es"] = "es"


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=200)
    comment: str | None = None
    language: Literal["en", "es"] = "es"


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cleaner_id: int
    created_at: datetime
    updated_at: datetime


class PaymentCreateSession(BaseModel):
    service_request_id: int
    amount: Decimal = Field(gt=0)
    currency: str = "USD"


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_request_id: int
    amount: Decimal
    currency: str
    provider: str
    provider_payment_id: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class PaymentSessionResponse(BaseModel):
    payment_id: int
    provider: str
    checkout_url: str | None = None
    client_secret: str | None = None
    provider_payment_id: str | None = None


class MatchResult(BaseModel):
    cleaner_id: int
    full_name: str
    average_rating: float
    years_experience: int
    services_offered: list[str]
    cities_neighborhoods: list[str]
    languages: list[str]
