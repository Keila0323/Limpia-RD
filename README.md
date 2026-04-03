# Limpia-RD 🧹
### Cleaning services marketplace for the Dominican Republic

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?logo=stripe&logoColor=white)
![OpenAI x Handshake](https://img.shields.io/badge/OpenAI_×_Handshake-Codex_Challenge-412991?logo=openai&logoColor=white)

Limpia-RD is a **full-stack REST API marketplace** connecting property owners and Airbnb hosts in the Dominican Republic with vetted cleaning and maintenance service providers — cleaners, laundry specialists, deep-clean crews, and handymen.

> **Entered in the [OpenAI × Handshake Codex national student competition](https://handshake.org).**

---

## Why I Built This

The Dominican Republic has a booming short-term rental market — Airbnbs, villas, and boutique hotels — but no reliable digital platform connecting hosts with trusted local service providers. Hosts rely on WhatsApp groups and word of mouth. I built Limpia-RD to solve that with a proper API: matching logic, reviews, ratings, and Stripe payments — the full marketplace stack.

---

## Live API

🔗 **[Swagger UI — Live Docs](https://limpia-rd.onrender.com/docs)** *(hosted on Render — may take ~30s to wake up)*

---

## Features

- **Cleaner profiles** — full CRUD, filterable by city, neighborhood, services offered, and language
- **Service requests** — hosts submit jobs with property type, location, schedule, and budget
- **Matching engine** — returns the best-fit cleaners for a given request
- **Reviews & ratings** — 5-star rating system with automatic score recalculation on every new review
- **Badges** — cleaners earn specialty badges (deep-clean expert, Airbnb pro, etc.) with images
- **Stripe payments** — checkout session creation + webhook to mark jobs as paid on completion
- **Bilingual API** — English/Spanish responses via `Accept-Language` header or `?lang=en|es`
- **Auto-generated API docs** — OpenAPI/Swagger and ReDoc out of the box

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| ORM | SQLAlchemy 2.0 + SQLite |
| Schema validation | Pydantic v2 |
| Payments | Stripe Checkout + webhooks |
| API Docs | OpenAPI / Swagger UI / ReDoc |
| Deployment | Render |

---

## Project Structure

```
Limpia-RD/
├── main.py          # FastAPI app + startup
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic request/response schemas
├── database.py      # DB session + engine setup
├── i18n.py          # English/Spanish translation logic
├── requirements.txt
└── routers/
    ├── cleaners.py  # Cleaner profiles + search + matching
    ├── requests.py  # Service request CRUD
    ├── reviews.py   # Reviews + ratings
    ├── payments.py  # Stripe checkout + webhook
    ├── badges.py    # Badge assignment
    └── utils.py
```

---

## Setup

```bash
git clone https://github.com/Keila0323/Limpia-RD.git
cd Limpia-RD
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export STRIPE_API_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
uvicorn main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

> SQLite DB (`limpia_rd.db`) is created automatically at first run.

---

## API Examples

**Register a cleaner**
```bash
curl -X POST http://127.0.0.1:8000/cleaners/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ana Perez",
    "bio": "Experienced Airbnb cleaner, Santo Domingo",
    "services_offered": ["cleaning", "deep-clean"],
    "cities_neighborhoods": ["Santo Domingo - Piantini"],
    "hourly_rate": 15,
    "years_experience": 5,
    "languages": ["es", "en"]
  }'
```

**Create a service request**
```bash
curl -X POST http://127.0.0.1:8000/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "host_id": 1,
    "location_city": "Santo Domingo",
    "property_type": "apartment",
    "service_type": "cleaning",
    "scheduled_datetime": "2026-05-10T14:00:00",
    "budget": 80
  }'
```

**Start a Stripe payment session**
```bash
curl -X POST http://127.0.0.1:8000/payments/create-session \
  -H "Content-Type: application/json" \
  -d '{"service_request_id": 1, "amount": 80, "currency": "USD"}'
```

---

Built by [Keila Olaverria](https://www.linkedin.com/in/keila-olaverria-56661493/) · Boston, MA
