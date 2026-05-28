"""Shared pytest fixtures for bot builder tests."""
from types import SimpleNamespace
import pytest


@pytest.fixture
def fake_bot_with_tools():
    """A minimal Bot-shaped object with tools enabled."""
    return SimpleNamespace(
        id="test-bot-id",
        name="Test Cairn",
        provider="anthropic",
        model="claude-opus-4-7",
        system_prompt="You are a test bot.",
        temperature=70,
        max_tokens=4096,
        api_key="sk-test-fake",
        api_key_id=None,
        api_key_ref=None,
        use_qdrant=False,
        qdrant_collection=None,
        qdrant_top_k=5,
        enable_memory=False,
        memory_max_messages=10,
        enable_suggestions=False,
        tools_enabled=["search_knowledge"],
        tool_config={
            "qdrant": {"collection": "sagerock", "top_k": 5},
            "cal_com": {"api_key_env": "CAL_COM_API_KEY",
                        "event_type_slug": "opportunity-call-30",
                        "username": "sage-lewis",
                        "timezone": "America/New_York"},
            "supabase": {"url_env": "SUPABASE_URL",
                         "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
                         "client_id": "test-client-uuid"},
            "escalation": {"to_email": "sage@sagerock.com"},
        },
    )


@pytest.fixture
def fake_bot_no_tools():
    """A Bot-shaped object with no tools (backwards-compat test)."""
    return SimpleNamespace(
        id="test-bot-id",
        name="Test Plain Bot",
        provider="anthropic",
        model="claude-opus-4-7",
        system_prompt="You are a test bot.",
        temperature=70,
        max_tokens=4096,
        api_key="sk-test-fake",
        api_key_id=None,
        api_key_ref=None,
        use_qdrant=False,
        qdrant_collection=None,
        qdrant_top_k=5,
        enable_memory=False,
        memory_max_messages=10,
        enable_suggestions=False,
        tools_enabled=[],
        tool_config={},
    )
