"""escalate_to_sage tool: email Sage when Cairn can't handle a request."""
import os
import logging
import httpx
from app.tools.base import Tool

logger = logging.getLogger(__name__)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def run(inputs: dict, config: dict) -> dict:
    """Email Sage with the conversation context and the reason for escalation.

    inputs: {reason, transcript}
    config: {"escalation": {"to_email"}, "sendgrid": {"api_key_env", "from_email"}}
    returns: {"sent": bool, "error"?}
    """
    sendgrid_cfg = config.get("sendgrid", {})
    api_key = os.getenv(sendgrid_cfg.get("api_key_env", "SENDGRID_API_KEY"))
    if not api_key:
        return {"sent": False, "error": "sendgrid_not_configured"}

    to_email = config.get("escalation", {}).get("to_email")
    from_email = sendgrid_cfg.get("from_email", "cairn@ask.sagerock.com")
    if not to_email:
        return {"sent": False, "error": "missing_to_email"}

    reason = inputs.get("reason", "(no reason given)")
    transcript = inputs.get("transcript", "")

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Cairn"},
        "subject": f"[Cairn escalation] {reason[:60]}",
        "content": [{
            "type": "text/plain",
            "value": (
                f"Cairn escalated a conversation to you.\n\n"
                f"Reason: {reason}\n\n"
                f"--- transcript ---\n{transcript}\n"
            ),
        }],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            SENDGRID_API_URL, json=payload, headers=headers, timeout=10.0,
        )
    except Exception as e:
        logger.warning(f"escalate_to_sage: request failed: {e}")
        return {"sent": False, "error": "sendgrid_unavailable"}

    if response.status_code in (200, 202):
        return {"sent": True}
    logger.warning(f"escalate_to_sage: sendgrid {response.status_code}: {response.text[:200]}")
    return {"sent": False, "error": f"sendgrid_http_{response.status_code}"}


TOOL = Tool(
    name="escalate_to_sage",
    description=(
        "Email Sage with the conversation when you cannot handle the visitor's request "
        "(complex custom work, sensitive topics, or system errors). Use sparingly. The "
        "visitor should be told 'Sage will reach out' after you call this."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Short description of why this needs Sage's attention.",
            },
            "transcript": {
                "type": "string",
                "description": "Recent conversation context (last 3-5 turns formatted as text).",
            },
        },
        "required": ["reason"],
    },
    run=run,
)
