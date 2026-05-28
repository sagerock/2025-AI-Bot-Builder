"""check_availability tool: query Cal.com for open booking slots."""
import os
import logging
import httpx
from app.tools.base import Tool

logger = logging.getLogger(__name__)

CAL_API_BASE = "https://api.cal.com/v2"


def run(inputs: dict, config: dict) -> dict:
    """Return open slots for the Cal.com event in the given date window.

    inputs: {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
    config: {"cal_com": {"api_key_env", "event_type_slug", "username", "timezone"}}
    returns: {"slots": [iso_string, ...]} or {"slots": [], "error": "..."}
    """
    cfg = config.get("cal_com", {})
    api_key_env = cfg.get("api_key_env", "CAL_COM_API_KEY")
    api_key = os.getenv(api_key_env)
    if not api_key:
        return {"slots": [], "error": "calcom_not_configured"}

    event_slug = cfg.get("event_type_slug")
    username = cfg.get("username")
    timezone = cfg.get("timezone", "America/New_York")
    start = inputs.get("start_date")
    end = inputs.get("end_date")
    if not start or not end:
        return {"slots": [], "error": "missing_date_range"}
    if not event_slug or not username:
        # Cal.com v2 /slots requires either eventTypeId or (eventTypeSlug+username).
        # We use the slug+username path; both must be set in tool_config.
        return {"slots": [], "error": "calcom_not_configured"}

    params = {
        "eventTypeSlug": event_slug,
        "username": username,
        "start": f"{start}T00:00:00.000Z",
        "end": f"{end}T23:59:59.999Z",
        "timeZone": timezone,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-09-04",
    }

    try:
        response = httpx.get(
            f"{CAL_API_BASE}/slots",
            params=params,
            headers=headers,
            timeout=10.0,
        )
        if response.status_code >= 400:
            logger.warning(f"check_availability: cal.com returned {response.status_code}")
            return {"slots": [], "error": f"calcom_http_{response.status_code}"}
        data = response.json()
    except Exception as e:
        logger.warning(f"check_availability: request failed: {e}")
        return {"slots": [], "error": "calcom_unavailable"}

    slots_by_day = data.get("data", {}).get("slots", {})
    slots = []
    for day_slots in slots_by_day.values():
        for slot in day_slots:
            t = slot.get("time")
            if t:
                slots.append(t)
    return {"slots": slots}


TOOL = Tool(
    name="check_availability",
    description=(
        "Check Sage's calendar for open 30-minute opportunity call slots in a date range. "
        "Returns ISO 8601 timestamps. Use before suggesting times to a visitor."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start of the search window, YYYY-MM-DD.",
            },
            "end_date": {
                "type": "string",
                "description": "End of the search window, YYYY-MM-DD.",
            },
        },
        "required": ["start_date", "end_date"],
    },
    run=run,
)
