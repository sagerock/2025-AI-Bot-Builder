"""Tests for capture_lead tool (Supabase contacts + cairn_sessions)."""
import os
from unittest.mock import patch, MagicMock
from app.tools import capture_lead


def test_upserts_contact_and_inserts_session():
    """capture_lead upserts to contacts and inserts a cairn_sessions row."""
    contact_resp = MagicMock()
    contact_resp.status_code = 201
    contact_resp.json.return_value = [{"id": "contact-uuid-1"}]

    session_resp = MagicMock()
    session_resp.status_code = 201
    session_resp.json.return_value = [{"id": "session-uuid-1"}]

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "service_test_key",
    }), patch("app.tools.capture_lead.httpx.post") as mock_post:
        mock_post.side_effect = [contact_resp, session_resp]

        result = capture_lead.TOOL.run(
            {
                "name": "Jane Principal",
                "email": "jane@maplevalley.org",
                "topic": "schools",
                "notes": "Wants admin center demo",
                "session_id": "chat-session-123",
            },
            {"supabase": {
                "url_env": "SUPABASE_URL",
                "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
                "client_id": "sagerock-client-uuid",
            }},
        )

    assert result["contact_id"] == "contact-uuid-1"
    assert result["session_row_id"] == "session-uuid-1"
    assert mock_post.call_count == 2  # one for contacts, one for cairn_sessions


def test_supabase_down_returns_error_but_does_not_raise():
    """capture_lead never blocks the conversation; returns an error code."""
    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "service_test_key",
    }), patch("app.tools.capture_lead.httpx.post") as mock_post:
        mock_post.side_effect = Exception("connection refused")

        result = capture_lead.TOOL.run(
            {"name": "Jane", "email": "jane@x.com", "topic": "x",
             "notes": "", "session_id": "s1"},
            {"supabase": {"url_env": "SUPABASE_URL",
                          "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
                          "client_id": "c"}},
        )

    assert result["captured"] is False
    assert result["error"] == "supabase_unavailable"


def test_missing_email_returns_error():
    """Email is required; missing it returns error without API call."""
    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "service_test_key",
    }), patch("app.tools.capture_lead.httpx.post") as mock_post:
        result = capture_lead.TOOL.run(
            {"name": "Jane", "topic": "x", "notes": "", "session_id": "s"},
            {"supabase": {"url_env": "SUPABASE_URL",
                          "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
                          "client_id": "c"}},
        )
    assert result == {"captured": False, "error": "missing_email"}
    mock_post.assert_not_called()
