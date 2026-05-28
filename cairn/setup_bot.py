"""Create (or update) the Cairn bot via the bot builder's REST API.

Usage:
    python cairn/setup_bot.py --base-url https://<your-bot-builder>.up.railway.app

Reads cairn/system_prompt.md and POSTs a complete Bot configuration. Reuses
the existing bot by name on subsequent runs (updates, doesn't duplicate).

Requires an admin auth cookie or token -- pass it via --auth-cookie or set
ADMIN_AUTH_COOKIE in the environment. The bot builder uses session cookies
for /api/bots, so log into /admin in a browser, copy the session cookie, and
pass it here.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "cairn" / "system_prompt.md"


def cairn_config() -> dict:
    """Return the full Bot create/update payload for Cairn."""
    return {
        "name": "Cairn",
        "description": "SageRock concierge - answers questions and books opportunity calls",
        "provider": "anthropic",
        "model": "claude-opus-4-7",
        "system_prompt": PROMPT_PATH.read_text(encoding="utf-8"),
        "temperature": 70,
        "max_tokens": 4096,
        "use_qdrant": False,  # RAG is now a tool, not always-on retrieval
        "qdrant_collection": None,
        "qdrant_top_k": 5,
        "enable_memory": True,
        "memory_max_messages": 20,
        "enable_suggestions": True,
        "widget_title": "Cairn",
        "widget_color": "#2c3e50",
        "widget_greeting": (
            "Hi, I'm Cairn, SageRock's guide. I can answer questions about our work with "
            "schools, law firms, email marketing, and AI bots, or book an opportunity call "
            "with Sage. What brings you by?"
        ),
        "tools_enabled": [
            "search_knowledge",
            "check_availability",
            "book_meeting",
            "capture_lead",
            "escalate_to_sage",
        ],
        "tool_config": {
            "qdrant": {"collection": "sagerock", "top_k": 5},
            "cal_com": {
                "api_key_env": "CAL_COM_API_KEY",
                "event_type_slug": "opportunity-call-30",
                "timezone": "America/New_York",
            },
            "supabase": {
                "url_env": "SUPABASE_URL",
                "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
                # SageRock client_id in the mail tool Supabase contacts table.
                "client_id": "dab0af79-80db-4e91-854c-be1b5ccd7288",
            },
            "escalation": {"to_email": "sage@sagerock.com"},
            "sendgrid": {
                "api_key_env": "SENDGRID_API_KEY",
                "from_email": "cairn@ask.sagerock.com",
            },
        },
        "suggested_prompts": [
            "Tell me about SageRock Schools",
            "I want to schedule a call",
            "What does SageRock do?",
            "Show me your AI bot tools",
        ],
    }


def find_existing(client: httpx.Client, base_url: str, name: str) -> str | None:
    response = client.get(f"{base_url}/api/bots")
    response.raise_for_status()
    for bot in response.json():
        if bot.get("name") == name:
            return bot["id"]
    return None


def setup(base_url: str, auth_cookie: str | None):
    cookies = {}
    if auth_cookie:
        # Format like "session=abc123" or just the value (try both)
        if "=" in auth_cookie:
            k, v = auth_cookie.split("=", 1)
            cookies[k] = v
        else:
            cookies["session"] = auth_cookie

    with httpx.Client(cookies=cookies, timeout=30.0) as client:
        existing_id = find_existing(client, base_url, "Cairn")
        payload = cairn_config()

        if existing_id:
            print(f"Updating existing Cairn (id={existing_id})...")
            response = client.put(f"{base_url}/api/bots/{existing_id}", json=payload)
        else:
            print("Creating new Cairn bot...")
            response = client.post(f"{base_url}/api/bots", json=payload)

        if response.status_code >= 400:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            sys.exit(1)

        bot = response.json()
        print(f"OK. Bot id: {bot.get('id')}")
        print(f"Chat URL: {base_url}/chat/{bot.get('id')}")
        print(f"Admin URL: {base_url}/admin#{bot.get('id')}")


def main():
    parser = argparse.ArgumentParser(description="Create or update the Cairn bot")
    parser.add_argument("--base-url", required=True,
                        help="Bot builder base URL (e.g. https://...up.railway.app)")
    parser.add_argument("--auth-cookie",
                        default=os.getenv("ADMIN_AUTH_COOKIE"),
                        help="Admin session cookie (or set ADMIN_AUTH_COOKIE env)")
    args = parser.parse_args()
    setup(args.base_url, args.auth_cookie)


if __name__ == "__main__":
    main()
