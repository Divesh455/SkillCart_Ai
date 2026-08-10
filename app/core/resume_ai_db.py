import json
import logging
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings

logger = logging.getLogger(__name__)

_engine: Optional[Engine] = None


def _get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    if not settings.RESUME_DATABASE_URL:
        raise ValueError("RESUME_DATABASE_URL setting is not configured.")

    _engine = create_engine(
        settings.RESUME_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=1800
    )
    return _engine


def _decode_json(value: Any) -> Any:
    while isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        value = json.loads(stripped)
    return value


def _extract_resume_payload(value: Any) -> Optional[dict]:
    payload = _decode_json(value)

    while isinstance(payload, dict):
        if "name" in payload and "contact" in payload:
            return payload

        for key in ("parsed_data", "resume", "data", "ai_response_json"):
            nested = payload.get(key)
            if nested:
                payload = _decode_json(nested)
                break
        else:
            return payload

    return None


def get_resume_ai_response_data(res_id: str) -> Optional[dict]:
    """Fetch only ai_response_json for a numeric resume_id from Railway Postgres."""
    try:
        resume_id = int(str(res_id).strip())
    except (TypeError, ValueError):
        return None

    query = text(
        """
        SELECT ai_response_json
        FROM public.resume
        WHERE resume_id = :resume_id
        LIMIT 1
        """
    )

    try:
        with _get_engine().connect() as connection:
            ai_response_json = connection.execute(
                query,
                {"resume_id": resume_id}
            ).scalar_one_or_none()
    except Exception as exc:
        logger.error("Failed to fetch ai_response_json for resume_id %s: %s", resume_id, exc)
        raise

    if not ai_response_json:
        return None

    return _extract_resume_payload(ai_response_json)
