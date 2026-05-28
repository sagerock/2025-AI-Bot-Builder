"""Tests for book_meeting tool (Cal.com booking creation)."""
import os
from unittest.mock import patch, MagicMock
from app.tools import book_meeting


def test_successful_booking_returns_confirmation():
    """A successful Cal.com booking returns confirmed=True with invite URL."""
    fake_response = MagicMock()
    fake_response.status_code = 201
    fake_response.json.return_value = {
        "data": {
            "uid": "booking-abc-123",
            "url": "https://cal.com/sage/opportunity-call-30/booking-abc-123",
        }
    }

    with patch.dict(os.environ, {"CAL_COM_API_KEY": "cal_test_key"}), \
         patch("app.tools.book_meeting.httpx.post") as mock_post:
        mock_post.return_value = fake_response

        result = book_meeting.TOOL.run(
            {
                "name": "Jane Principal",
                "email": "jane@maplevalley.org",
                "start_time": "2026-06-01T14:00:00.000Z",
                "topic": "Maple Valley Waldorf intro",
                "notes": "Wants admin center demo",
            },
            {"cal_com": {
                "api_key_env": "CAL_COM_API_KEY",
                "event_type_slug": "opportunity-call-30",
                "timezone": "America/New_York",
            }},
        )

    assert result["confirmed"] is True
    assert result["booking_id"] == "booking-abc-123"
    assert "cal.com" in result["invite_url"]


def test_slot_taken_returns_error():
    """When the slot is no longer available, return confirmed=False with reason."""
    fake_response = MagicMock()
    fake_response.status_code = 409
    fake_response.json.return_value = {"error": "slot_unavailable"}
    fake_response.text = "Slot unavailable"

    with patch.dict(os.environ, {"CAL_COM_API_KEY": "cal_test_key"}), \
         patch("app.tools.book_meeting.httpx.post") as mock_post:
        mock_post.return_value = fake_response

        result = book_meeting.TOOL.run(
            {
                "name": "Jane",
                "email": "jane@example.com",
                "start_time": "2026-06-01T14:00:00.000Z",
                "topic": "test",
            },
            {"cal_com": {"api_key_env": "CAL_COM_API_KEY",
                          "event_type_slug": "opportunity-call-30",
                          "timezone": "America/New_York"}},
        )

    assert result["confirmed"] is False
    assert result["error"] == "slot_unavailable"


def test_missing_required_fields():
    """Missing name or email returns error without API call."""
    with patch.dict(os.environ, {"CAL_COM_API_KEY": "cal_test_key"}), \
         patch("app.tools.book_meeting.httpx.post") as mock_post:
        result = book_meeting.TOOL.run(
            {"email": "jane@x.com", "start_time": "2026-06-01T14:00:00.000Z", "topic": "x"},
            {"cal_com": {"api_key_env": "CAL_COM_API_KEY",
                          "event_type_slug": "opportunity-call-30",
                          "timezone": "America/New_York"}},
        )

    assert result == {"confirmed": False, "error": "missing_required_fields"}
    mock_post.assert_not_called()
