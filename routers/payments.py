import os

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from i18n import get_lang, t
from models import Payment, ServiceRequest
from schemas import PaymentCreateSession, PaymentSessionResponse

router = APIRouter(prefix="/payments", tags=["payments"])

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY


@router.post("/create-session", response_model=PaymentSessionResponse)
def create_payment_session(
    payload: PaymentCreateSession,
    request: Request,
    lang: str | None = None,
    db: Session = Depends(get_db),
):
    locale = get_lang(request, lang)
    service_request = db.get(ServiceRequest, payload.service_request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail=t("request_not_found", locale))

    if not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail=t("stripe_not_configured", locale))

    # TODO: wire FRONTEND_SUCCESS_URL / FRONTEND_CANCEL_URL via secure env config.
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": payload.currency.lower(),
                    "product_data": {"name": f"Limpia-RD Service Request #{payload.service_request_id}"},
                    "unit_amount": int(float(payload.amount) * 100),
                },
                "quantity": 1,
            }
        ],
        success_url="https://example.com/payments/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://example.com/payments/cancel",
        metadata={"service_request_id": str(payload.service_request_id)},
    )

    payment = Payment(
        service_request_id=payload.service_request_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        provider="stripe",
        provider_payment_id=session.id,
        status="created",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentSessionResponse(
        payment_id=payment.id,
        provider="stripe",
        checkout_url=session.url,
        provider_payment_id=session.id,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    payload = await request.body()

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Missing STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        provider_id = session.get("id")

        payment = db.query(Payment).filter(Payment.provider_payment_id == provider_id).first()
        if payment:
            payment.status = "succeeded"
            db.add(payment)
            service_request = db.get(ServiceRequest, payment.service_request_id)
            if service_request:
                service_request.status = "paid"
                db.add(service_request)
            db.commit()

    return {"received": True}
