from fastapi import Request

MESSAGES: dict[str, dict[str, str]] = {
    "not_found": {
        "en": "Resource not found",
        "es": "Recurso no encontrado",
    },
    "cleaner_not_found": {
        "en": "Cleaner not found",
        "es": "Proveedor no encontrado",
    },
    "request_not_found": {
        "en": "Service request not found",
        "es": "Solicitud de servicio no encontrada",
    },
    "invalid_status_for_review": {
        "en": "Reviews can only be created for paid or completed requests",
        "es": "Las reseñas solo se pueden crear para solicitudes pagadas o completadas",
    },
    "invalid_request_relation": {
        "en": "Service request does not belong to this host",
        "es": "La solicitud de servicio no pertenece a este anfitrión",
    },
    "stripe_not_configured": {
        "en": "Stripe is not configured. Set STRIPE_API_KEY.",
        "es": "Stripe no está configurado. Define STRIPE_API_KEY.",
    },
}


def get_lang(request: Request, lang: str | None = None) -> str:
    if lang in {"en", "es"}:
        return lang

    header = request.headers.get("accept-language", "")
    primary = header.split(",")[0].split("-")[0].strip().lower()
    return primary if primary in {"en", "es"} else "en"


def t(message_key: str, lang: str) -> str:
    return MESSAGES.get(message_key, {}).get(lang) or MESSAGES.get(message_key, {}).get(
        "en", message_key
    )
