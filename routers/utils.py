from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Cleaner, Review


def list_to_csv(values: list[str]) -> str:
    return ",".join(v.strip() for v in values if v and v.strip())


def csv_to_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()] if value else []


def recalc_cleaner_rating(db: Session, cleaner_id: int) -> None:
    avg_rating, count = db.query(func.avg(Review.rating), func.count(Review.id)).filter(
        Review.cleaner_id == cleaner_id
    ).one()
    cleaner = db.get(Cleaner, cleaner_id)
    if cleaner is None:
        return
    cleaner.average_rating = float(avg_rating or 0.0)
    cleaner.review_count = int(count or 0)
    db.add(cleaner)
    db.commit()
