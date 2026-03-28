from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from i18n import get_lang, t
from models import Cleaner
from schemas import CleanerCreate, CleanerDetail, CleanerRead
from routers.utils import csv_to_list, list_to_csv

router = APIRouter(prefix="/cleaners", tags=["cleaners"])


def to_cleaner_read(cleaner: Cleaner) -> CleanerRead:
    return CleanerRead(
        id=cleaner.id,
        full_name=cleaner.full_name,
        bio=cleaner.bio,
        services_offered=csv_to_list(cleaner.services_offered),
        cities_neighborhoods=csv_to_list(cleaner.cities_neighborhoods),
        hourly_rate=cleaner.hourly_rate,
        flat_rate=cleaner.flat_rate,
        years_experience=cleaner.years_experience,
        languages=csv_to_list(cleaner.languages),
        average_rating=cleaner.average_rating,
        review_count=cleaner.review_count,
        created_at=cleaner.created_at,
        updated_at=cleaner.updated_at,
    )


@router.post("/", response_model=CleanerRead)
def create_cleaner(payload: CleanerCreate, db: Session = Depends(get_db)):
    cleaner = Cleaner(
        full_name=payload.full_name,
        bio=payload.bio,
        services_offered=list_to_csv(payload.services_offered),
        cities_neighborhoods=list_to_csv(payload.cities_neighborhoods),
        hourly_rate=payload.hourly_rate,
        flat_rate=payload.flat_rate,
        years_experience=payload.years_experience,
        languages=list_to_csv(payload.languages),
    )
    db.add(cleaner)
    db.commit()
    db.refresh(cleaner)
    return to_cleaner_read(cleaner)


@router.get("/", response_model=list[CleanerRead])
def list_cleaners(
    city: str | None = None,
    service_type: str | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5),
    language: str | None = Query(default=None, pattern="^(en|es)$"),
    db: Session = Depends(get_db),
):
    cleaners = db.query(Cleaner).all()
    results: list[CleanerRead] = []
    for cleaner in cleaners:
        cities = csv_to_list(cleaner.cities_neighborhoods)
        services = csv_to_list(cleaner.services_offered)
        langs = csv_to_list(cleaner.languages)

        if city and not any(city.lower() in c.lower() for c in cities):
            continue
        if service_type and not any(service_type.lower() in s.lower() for s in services):
            continue
        if min_rating is not None and cleaner.average_rating < min_rating:
            continue
        if language and language not in langs:
            continue
        results.append(to_cleaner_read(cleaner))
    return results


@router.get("/{cleaner_id}", response_model=CleanerDetail)
def get_cleaner(
    cleaner_id: int,
    request: Request,
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)
    cleaner = db.get(Cleaner, cleaner_id)
    if cleaner is None:
        raise HTTPException(status_code=404, detail=t("cleaner_not_found", locale))

    detail = CleanerDetail(**to_cleaner_read(cleaner).model_dump(), badges=cleaner.badges)
    return detail
