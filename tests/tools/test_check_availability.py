"""Tests for check_availability tool (Cal.com integration)."""
import os
from unittest.mock import patch, MagicMock
from app.tools import check_availability


def test_returns_iso_slots_on_success():
    """check_availability hits Cal.com API and returns ISO timestamps."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "data": {
            "slots": {
                "2026-06-01": [
                    {"time": "2026-06-01T14:00:00.000Z"},
                    {"time": "2026-06-01T15:00:00.000Z"},
                ],
                "2026-06-02": [
                    {"time": "2026-06-02T10:00:00.000Z"},
                ],
            }
        }
    }

    with patch.dict(os.environ, {"CAL_COM_API_KEY": "cal_test_key"}), \
         patch("app.tools.check_availability.httpx.get") as mock_get:
        mock_get.return_value = fake_response

        result = check_availability.TOOL.run(
            {"start_date": "2026-06-01", "end_date": "2026-06-02"},
            {"cal_com": {
                "api_key_env": "CAL_COM_API_KEY",
                "event_type_slug": "opportunity-call-30",
                "timezone": "America/New_York",
            }},
        )

    assert result["slots"] == [
        "2026-06-01T14:00:00.000Z",
        "2026-06-01T15:00:00.000Z",
        "2026-06-02T10:00:00.000Z",
    ]
    # Verify it called the right endpoint
    args, kwargs = mock_get.call_args
    assert "slots" in args[0] or "slots" in kwargs.get("url", "")


def test_returns_empty_on_api_error():
    """When Cal.com is unreachable, return empty slots with an error code."""
    with patch.dict(os.environ, {"CAL_COM_API_KEY": "cal_test_key"}), \
         patch("app.tools.check_availability.httpx.get") as mock_get:
        mock_get.side_effect = Exception("connection refused")

        result = check_availability.TOOL.run(
            {"start_date": "2026-06-01", "end_date": "2026-06-02"},
            {"cal_com": {"api_key_env": "CAL_COM_API_KEY",
                          "event_type_slug": "opportunity-call-30",
                          "timezone": "America/New_York"}},
        )

    assert result == {"slots": [], "error": "calcom_unavailable"}


def test_returns_empty_when_api_key_missing():
    """No API key configured -> graceful empty result."""
    with patch.dict(os.environ, {}, clear=True):
        result = check_availability.TOOL.run(
            {"start_date": "2026-06-01", "end_date": "2026-06-02"},
            {"cal_com": {"api_key_env": "CAL_COM_API_KEY",
                          "event_type_slug": "opportunity-call-30",
                          "timezone": "America/New_York"}},
        )
    assert result == {"slots": [], "error": "calcom_not_configured"}
