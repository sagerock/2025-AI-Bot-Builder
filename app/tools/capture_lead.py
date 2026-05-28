"""capture_lead tool: upsert a contact and record a cairn_sessions row in Supabase."""
import os
import logging
import httpx
from app.tools.base import Tool

logger = logging.getLogger(__name__)


def run(inputs: dict, config: dict) -> dict:
    """Upsert into contacts (by email), insert into cairn_sessions.

    inputs: {name, email, topic, notes, session_id}
    config: {"supabase": {"url_env", "service_key_env", "client_id"}}
    returns: {"contact_id", "session_row_id", "captured": True}
             or {"captured": False, "error": "..."}
    """
    cfg = config.get("supabase", {})
    url = os.getenv(cfg.get("url_env", "SUPABASE_URL"))
    key = os.getenv(cfg.get("service_key_env", "SUPABASE_SERVICE_ROLE_KEY"))
    client_id = cfg.get("client_id")

    if not (url and key and client_id):
        return {"captured": False, "error": "supabase_not_configured"}

    name = inputs.get("name", "").strip()
    email = inputs.get("email", "").strip()
    topic = inputs.get("topic", "")
    notes = inputs.get("notes", "")
    session_id = inputs.get("session_id", "")

    if not email:
        return {"captured": False, "error": "missing_email"}

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates",
    }

    try:
        # Upsert contact (by email)
        contact_payload = {
            "client_id": client_id,
            "email": email,
            "name": name,
            "source": "cairn",
        }
        contact_resp = httpx.post(
            f"{url}/rest/v1/contacts?on_conflict=email",
            json=contact_payload,
            headers=headers,
            timeout=10.0,
        )
        if contact_resp.status_code >= 400:
            logger.warning(
                f"capture_lead: contacts upsert {contact_resp.status_code}: "
                f"{contact_resp.text[:200]}"
            )
            return {"captured": False, "error": f"contacts_http_{contact_resp.status_code}"}
        contact_data = contact_resp.json()
        contact_id = contact_data[0]["id"] if contact_data else None

        # Insert cairn_sessions row
        session_payload = {
            "session_id": session_id,
            "contact_id": contact_id,
            "topic": topic,
            "outcome": "captured",
            "transcript": {"notes": notes},
        }
        session_resp = httpx.post(
            f"{url}/rest/v1/cairn_sessions",
            json=session_payload,
            headers=headers,
            timeout=10.0,
        )
        if session_resp.status_code >= 400:
            logger.warning(
                f"capture_lead: cairn_sessions insert {session_resp.status_code}"
            )
            return {
                "captured": True,
                "contact_id": contact_id,
                "session_row_id": None,
                "error": "session_insert_failed",
            }
        session_data = session_resp.json()
        session_row_id = session_data[0]["id"] if session_data else None

        return {
            "captured": True,
            "contact_id": contact_id,
            "session_row_id": session_row_id,
        }
    except Exception as e:
        logger.warning(f"capture_lead: request failed: {e}")
        return {"captured": False, "error": "supabase_unavailable"}


TOOL = Tool(
    name="capture_lead",
    description=(
        "Save the visitor as a lead in SageRock's CRM. Call this when the visitor shares "
        "their name and email and shows real interest, even if they don't book a meeting. "
        "Idempotent on email — safe to call multiple times for the same person."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "topic": {
                "type": "string",
                "description": "Primary topic of interest (e.g. 'schools', 'mail-tool', 'general').",
            },
            "notes": {
                "type": "string",
                "description": "Short summary of what the visitor said they need.",
            },
            "session_id": {
                "type": "string",
                "description": "Current chat session ID for audit trail.",
            },
        },
        "required": ["email", "session_id"],
    },
    run=run,
)
