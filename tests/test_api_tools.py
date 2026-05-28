"""Tests for GET /api/tools."""
from fastapi.testclient import TestClient
from app.main import app


def test_returns_registered_tools():
    """GET /api/tools returns all registered tools with name, description, and input schema."""
    client = TestClient(app)
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [t["name"] for t in data]
    expected = {"search_knowledge", "check_availability", "book_meeting", "capture_lead", "escalate_to_sage"}
    assert expected.issubset(set(names))
    for tool in data:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"
