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

    if not isinstance(payload, dict):
        return None

    # Your parsed_json structure:
    # {
    #     "success": true,
    #     "message": "Success",
    #     "data": {
    #         "name": "...",
    #         "contact": {...}
    #     }
    # }

    if isinstance(payload.get("data"), dict):
        return payload["data"]

    # Fallback if the JSON is already in ResumeSchema format
    if "name" in payload and "contact" in payload:
        return payload

    return None


def get_resume_ai_response_data(res_id: str) -> Optional[dict]:
    """Fetch only parsed_json for a numeric resume_id from Railway Postgres."""
    try:
        resume_id = int(str(res_id).strip())
    except (TypeError, ValueError):
        return None

    query = text(
        """
        SELECT parsed_json
        FROM public.resume_entity
        WHERE id = :resume_id
        LIMIT 1
        """
    )

    try:
        with _get_engine().connect() as connection:
            parsed_json = connection.execute(
                query,
                {"resume_id": resume_id}
            ).scalar_one_or_none()
    except Exception as exc:
        logger.error("Failed to fetch parsed_json for resume_id %s: %s", resume_id, exc)
        raise

    if not parsed_json:
        return None

    return _extract_resume_payload(parsed_json)
