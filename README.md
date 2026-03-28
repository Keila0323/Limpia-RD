# Limpia-RD Marketplace Backend (FastAPI)

Backend API for **Limpia-RD**, a marketplace connecting property owners/managers in the Dominican Republic with cleaning and property service providers.

## Features

- Service providers (cleaners) CRUD basics with filters
- Service requests for hosts/clients
- Matching endpoint for best cleaners
- Badges with images for cleaners
- Reviews & ratings with automatic cleaner score recalculation
- Stripe-friendly payment session + webhook flow
- Lightweight i18n for English/Spanish (`Accept-Language` header or `?lang=en|es`)

## Project structure

```text
.
├── database.py
├── i18n.py
├── main.py
├── models.py
├── requirements.txt
├── schemas.py
└── routers/
    ├── badges.py
    ├── cleaners.py
    ├── payments.py
    ├── requests.py
    ├── reviews.py
    └── utils.py
```

## Setup

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Set environment variables (Stripe)

```bash
export STRIPE_API_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
```

> Do not commit real keys. Use environment variables only.

### 4) Run the API

```bash
uvicorn main:app --reload
```

Open docs at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example requests

### Create a cleaner

```bash
curl -X POST http://127.0.0.1:8000/cleaners/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ana Perez",
    "bio": "Experienced cleaner for Airbnb and villas",
    "services_offered": ["cleaning", "deep-clean"],
    "cities_neighborhoods": ["Santo Domingo - Piantini", "Santo Domingo"],
    "hourly_rate": 15,
    "flat_rate": 60,
    "years_experience": 5,
    "languages": ["es", "en"]
  }'
```

### Create a service request

```bash
curl -X POST http://127.0.0.1:8000/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "host_id": 123,
    "location_city": "Santo Domingo",
    "location_neighborhood": "Piantini",
    "property_type": "apartment",
    "service_type": "cleaning",
    "scheduled_datetime": "2030-01-10T14:00:00",
    "budget": 80,
    "special_instructions": "Bring eco products",
    "status": "pending"
  }'
```

### Create a review (request must be paid/completed)

```bash
curl -X POST http://127.0.0.1:8000/cleaners/1/reviews/ \
  -H "Content-Type: application/json" \
  -H "Accept-Language: en" \
  -d '{
    "host_id": 123,
    "service_request_id": 1,
    "rating": 5,
    "title": "Great service",
    "comment": "On time and very thorough",
    "language": "en"
  }'
```

### Start a payment session

```bash
curl -X POST http://127.0.0.1:8000/payments/create-session \
  -H "Content-Type: application/json" \
  -d '{
    "service_request_id": 1,
    "amount": 80,
    "currency": "USD"
  }'
```

## Notes

- SQLite DB file is created as `limpia_rd.db` at runtime.
- `POST /payments/webhook` updates payment status to `succeeded` and service request status to `paid` when Stripe checkout session completes.
- TODO: replace hardcoded success/cancel URLs with env vars for your frontend.
