"""book_meeting tool: create a Cal.com booking."""
import os
import logging
import httpx
from app.tools.base import Tool

logger = logging.getLogger(__name__)

CAL_API_BASE = "https://api.cal.com/v2"


def run(inputs: dict, config: dict) -> dict:
    """Create a Cal.com booking.

    inputs: {name, email, start_time, topic, notes (optional)}
    config: {"cal_com": {"api_key_env", "event_type_slug", "timezone"}}
    returns: {confirmed: bool, booking_id?, invite_url?, error?}
    """
    cfg = config.get("cal_com", {})
    api_key = os.getenv(cfg.get("api_key_env", "CAL_COM_API_KEY"))
    if not api_key:
        return {"confirmed": False, "error": "calcom_not_configured"}

    name = inputs.get("name", "").strip()
    email = inputs.get("email", "").strip()
    start_time = inputs.get("start_time", "").strip()
    topic = inputs.get("topic", "Opportunity Call")
    notes = inputs.get("notes", "")

    if not (name and email and start_time):
        return {"confirmed": False, "error": "missing_required_fields"}

    payload = {
        "eventTypeSlug": cfg.get("event_type_slug", "opportunity-call-30"),
        "start": start_time,
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": cfg.get("timezone", "America/New_York"),
        },
        "metadata": {"topic": topic, "notes": notes, "source": "cairn"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-08-13",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            f"{CAL_API_BASE}/bookings",
            json=payload,
            headers=headers,
            timeout=15.0,
        )
    except Exception as e:
        logger.warning(f"book_meeting: request failed: {e}")
        return {"confirmed": False, "error": "calcom_unavailable"}

    if response.status_code in (200, 201):
        data = response.json().get("data", {})
        return {
            "confirmed": True,
            "booking_id": data.get("uid", ""),
            "invite_url": data.get("url", ""),
        }

    # Handle known error codes
    if response.status_code == 409:
        return {"confirmed": False, "error": "slot_unavailable"}
    if response.status_code == 422:
        return {"confirmed": False, "error": "validation_failed"}

    logger.warning(f"book_meeting: cal.com {response.status_code}: {response.text[:200]}")
    return {"confirmed": False, "error": f"calcom_http_{response.status_code}"}


TOOL = Tool(
    name="book_meeting",
    description=(
        "Book a 30-minute opportunity call with Sage at a specific time. "
        "Only call this once you have the visitor's name, email, and a confirmed start time "
        "from check_availability. Returns confirmation with an invite URL or an error reason."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Visitor's full name."},
            "email": {"type": "string", "description": "Visitor's email address."},
            "start_time": {
                "type": "string",
                "description": "ISO 8601 timestamp from check_availability (e.g. 2026-06-01T14:00:00.000Z).",
            },
            "topic": {
                "type": "string",
                "description": "Short topic for the call (e.g. 'Schools intro' or 'Mail tool demo').",
            },
            "notes": {
                "type": "string",
                "description": "Optional context from the conversation to help Sage prep.",
            },
        },
        "required": ["name", "email", "start_time", "topic"],
    },
    run=run,
)
