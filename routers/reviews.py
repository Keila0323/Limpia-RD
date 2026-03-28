from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from i18n import get_lang, t
from models import Cleaner, Review, ServiceRequest
from schemas import ReviewCreate, ReviewRead, ReviewUpdate
from routers.utils import recalc_cleaner_rating

router = APIRouter(tags=["reviews"])


@router.post("/cleaners/{cleaner_id}/reviews/", response_model=ReviewRead)
def create_review(
    cleaner_id: int,
    payload: ReviewCreate,
    request: Request,
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)

    cleaner = db.get(Cleaner, cleaner_id)
    if cleaner is None:
        raise HTTPException(status_code=404, detail=t("cleaner_not_found", locale))

    service_request = db.get(ServiceRequest, payload.service_request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail=t("request_not_found", locale))

    if service_request.host_id != payload.host_id:
        raise HTTPException(status_code=400, detail=t("invalid_request_relation", locale))

    if service_request.status not in {"paid", "completed"}:
        raise HTTPException(status_code=400, detail=t("invalid_status_for_review", locale))

    review = Review(cleaner_id=cleaner_id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    recalc_cleaner_rating(db, cleaner_id)
    db.refresh(review)
    return review


@router.get("/cleaners/{cleaner_id}/reviews/", response_model=list[ReviewRead])
def list_reviews(
    cleaner_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    return (
        db.query(Review)
        .filter(Review.cleaner_id == cleaner_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


@router.put("/reviews/{review_id}", response_model=ReviewRead)
def update_review(review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    for key, value in payload.model_dump().items():
        setattr(review, key, value)
    db.add(review)
    db.commit()
    db.refresh(review)
    recalc_cleaner_rating(db, review.cleaner_id)
    return review


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    cleaner_id = review.cleaner_id
    db.delete(review)
    db.commit()
    recalc_cleaner_rating(db, cleaner_id)
    return {"message": "ok"}
