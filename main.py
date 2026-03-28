from fastapi import FastAPI

from database import Base, engine
from routers import badges, cleaners, payments, requests, reviews

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Limpia-RD Marketplace API", version="1.0.0")

app.include_router(cleaners.router)
app.include_router(badges.router)
app.include_router(requests.router)
app.include_router(reviews.router)
app.include_router(payments.router)


@app.get("/")
def root():
    return {"message": "Limpia-RD API is running"}
