from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from i18n import get_lang, t
from models import Cleaner, ServiceRequest
from schemas import MatchResult, ServiceRequestCreate, ServiceRequestRead
from routers.utils import csv_to_list

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/", response_model=ServiceRequestRead)
def create_request(payload: ServiceRequestCreate, db: Session = Depends(get_db)):
    service_request = ServiceRequest(**payload.model_dump())
    db.add(service_request)
    db.commit()
    db.refresh(service_request)
    return service_request


@router.get("/", response_model=list[ServiceRequestRead])
def list_requests(
    status: str | None = None,
    city: str | None = None,
    service_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(ServiceRequest)
    if status:
        query = query.filter(ServiceRequest.status == status)
    if city:
        query = query.filter(ServiceRequest.location_city.ilike(f"%{city}%"))
    if service_type:
        query = query.filter(ServiceRequest.service_type.ilike(f"%{service_type}%"))
    return query.order_by(ServiceRequest.scheduled_datetime.asc()).all()


@router.get("/{request_id}", response_model=ServiceRequestRead)
def get_request(
    request_id: int,
    request: Request,
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)
    service_request = db.get(ServiceRequest, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail=t("request_not_found", locale))
    return service_request


@router.get("/{request_id}/matches", response_model=list[MatchResult])
def get_matches(
    request_id: int,
    request: Request,
    top_n: int = Query(default=3, ge=1, le=20),
    preferred_language: str | None = Query(default=None, pattern="^(en|es)$"),
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)
    service_request = db.get(ServiceRequest, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail=t("request_not_found", locale))

    candidates = db.query(Cleaner).all()
    filtered: list[Cleaner] = []
    for cleaner in candidates:
        services = csv_to_list(cleaner.services_offered)
        locations = csv_to_list(cleaner.cities_neighborhoods)

        has_service = any(service_request.service_type.lower() in s.lower() for s in services)
        in_area = any(
            service_request.location_city.lower() in loc.lower()
            or service_request.location_neighborhood.lower() in loc.lower()
            for loc in locations
        )
        language_ok = True
        if preferred_language:
            language_ok = preferred_language in csv_to_list(cleaner.languages)

        if has_service and in_area and language_ok:
            filtered.append(cleaner)

    filtered.sort(key=lambda c: (c.average_rating, c.years_experience), reverse=True)
    selected = filtered[:top_n]
    return [
        MatchResult(
            cleaner_id=c.id,
            full_name=c.full_name,
            average_rating=c.average_rating,
            years_experience=c.years_experience,
            services_offered=csv_to_list(c.services_offered),
            cities_neighborhoods=csv_to_list(c.cities_neighborhoods),
            languages=csv_to_list(c.languages),
        )
        for c in selected
    ]
