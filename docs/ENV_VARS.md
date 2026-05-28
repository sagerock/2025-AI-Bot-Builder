# Environment variables

The bot builder reads these from the environment at runtime. Tools that depend on
external services return graceful error codes if their required vars are missing.

## Core (existing)

| Var | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (sqlite or postgres) |
| `DEFAULT_ANTHROPIC_API_KEY` | Fallback Anthropic key when bot.api_key is unset |
| `DEFAULT_OPENAI_API_KEY` | Fallback OpenAI key |
| `QDRANT_URL` | Qdrant cluster URL |
| `QDRANT_API_KEY` | Qdrant API key |

## Added for Cairn

| Var | Purpose | Set when |
|---|---|---|
| `CAL_COM_API_KEY` | Cal.com personal API key (read at api.cal.com/v2) | A bot uses `check_availability` or `book_meeting` |
| `SUPABASE_URL` | Supabase project URL for lead capture | A bot uses `capture_lead` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service-role key (server-side only, never expose) | A bot uses `capture_lead` |
| `SENDGRID_API_KEY` | SendGrid API key for escalation emails | A bot uses `escalate_to_sage` |

## Per-bot configuration (stored in `bots.tool_config` JSON, not env)

- Which Supabase `client_id` to attribute leads to
- Which Cal.com `event_type_slug` and `timezone` to use
- Escalation `to_email`
- Qdrant `collection` name and `top_k`

Example `tool_config` for Cairn:

```json
{
  "qdrant": {"collection": "sagerock", "top_k": 5},
  "cal_com": {
    "api_key_env": "CAL_COM_API_KEY",
    "event_type_slug": "opportunity-call-30",
    "timezone": "America/New_York"
  },
  "supabase": {
    "url_env": "SUPABASE_URL",
    "service_key_env": "SUPABASE_SERVICE_ROLE_KEY",
    "client_id": "<sagerock client uuid in mail tool Supabase>"
  },
  "escalation": {"to_email": "sage@sagerock.com"},
  "sendgrid": {
    "api_key_env": "SENDGRID_API_KEY",
    "from_email": "cairn@ask.sagerock.com"
  }
}
```
