from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from i18n import get_lang, t
from models import Badge, Cleaner
from schemas import BadgeCreate, BadgeRead

router = APIRouter(tags=["badges"])


@router.post("/cleaners/{cleaner_id}/badges/", response_model=BadgeRead)
def create_badge(cleaner_id: int, payload: BadgeCreate, db: Session = Depends(get_db)):
    cleaner = db.get(Cleaner, cleaner_id)
    if cleaner is None:
        raise HTTPException(status_code=404, detail="Cleaner not found")

    badge = Badge(cleaner_id=cleaner_id, **payload.model_dump())
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.get("/cleaners/{cleaner_id}/badges/", response_model=list[BadgeRead])
def list_badges(cleaner_id: int, db: Session = Depends(get_db)):
    return db.query(Badge).filter(Badge.cleaner_id == cleaner_id).all()


@router.delete("/badges/{badge_id}")
def delete_badge(
    badge_id: int,
    request: Request,
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)
    badge = db.get(Badge, badge_id)
    if badge is None:
        raise HTTPException(status_code=404, detail=t("not_found", locale))
    db.delete(badge)
    db.commit()
    return {"message": "ok"}
