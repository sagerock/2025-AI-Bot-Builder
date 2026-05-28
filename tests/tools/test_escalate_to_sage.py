"""Tests for escalate_to_sage tool (SendGrid email)."""
import os
from unittest.mock import patch, MagicMock
from app.tools import escalate_to_sage


def test_sends_email_via_sendgrid():
    """escalate_to_sage calls SendGrid API with the transcript and reason."""
    fake_response = MagicMock()
    fake_response.status_code = 202

    with patch.dict(os.environ, {"SENDGRID_API_KEY": "SG.test"}), \
         patch("app.tools.escalate_to_sage.httpx.post") as mock_post:
        mock_post.return_value = fake_response

        result = escalate_to_sage.TOOL.run(
            {
                "reason": "Visitor asked about pricing for 5 schools simultaneously",
                "transcript": "User: hi\nCairn: hi!\nUser: ...",
            },
            {"escalation": {"to_email": "sage@sagerock.com"},
             "sendgrid": {"api_key_env": "SENDGRID_API_KEY",
                           "from_email": "cairn@ask.sagerock.com"}},
        )

    assert result["sent"] is True
    args, kwargs = mock_post.call_args
    assert "sendgrid.com" in args[0]
    payload = kwargs["json"]
    assert payload["personalizations"][0]["to"][0]["email"] == "sage@sagerock.com"


def test_returns_error_on_sendgrid_failure():
    """When SendGrid is unreachable, return sent=False."""
    with patch.dict(os.environ, {"SENDGRID_API_KEY": "SG.test"}), \
         patch("app.tools.escalate_to_sage.httpx.post") as mock_post:
        mock_post.side_effect = Exception("connection refused")

        result = escalate_to_sage.TOOL.run(
            {"reason": "x", "transcript": "y"},
            {"escalation": {"to_email": "sage@sagerock.com"},
             "sendgrid": {"api_key_env": "SENDGRID_API_KEY",
                           "from_email": "cairn@ask.sagerock.com"}},
        )

    assert result == {"sent": False, "error": "sendgrid_unavailable"}


def test_returns_error_when_api_key_missing():
    """No SendGrid key configured -> sent=False, no API call."""
    with patch.dict(os.environ, {}, clear=True), \
         patch("app.tools.escalate_to_sage.httpx.post") as mock_post:
        result = escalate_to_sage.TOOL.run(
            {"reason": "x", "transcript": "y"},
            {"escalation": {"to_email": "sage@sagerock.com"},
             "sendgrid": {"api_key_env": "SENDGRID_API_KEY",
                           "from_email": "cairn@ask.sagerock.com"}},
        )
    assert result == {"sent": False, "error": "sendgrid_not_configured"}
    mock_post.assert_not_called()
