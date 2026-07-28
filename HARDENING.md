# Hardening punch list

Findings from 2026-07-28, the day the AWSNA bots migrated here from Flowise and the
platform got a real shakedown (Sonnet 5 support, citation links, per-bot Full Document
toggle all landed that day). Everything below is a known, bounded gap — none are
architectural. Ordered by value.

## 1. Session storage (highest priority)
`app/auth.py` keeps admin sessions in a process-local dict, so **every deploy or restart
logs the admin out**, and >1 uvicorn worker/replica would break login entirely (requests
hit a worker that never saw the session). Replace with signed-cookie sessions
(itsdangerous) or a `sessions` table in Postgres. Small, self-contained change.

## 2. Streaming responses
Chat waits for the full completion, then renders. With reasoning models (Sonnet 5,
GPT-5) the silent pause is long. Add SSE streaming: `client.messages.stream()` /
OpenAI streaming → StreamingResponse → incremental render in `chat.html` and
`widget.js`. Biggest UX win on the list.

## 3. Replace the hand-rolled markdown parser
`chat.html` `parseMarkdown()` is custom regex. It's already produced two real bugs
(links not rendered at all; placeholder tokens eaten by the italic rule — both fixed
2026-07-28). Swap for marked or markdown-it + DOMPurify, keep the http/https-only link
policy. Do the same in `widget.js` if it renders markdown.

## 4. Minimal test suite
No tests exist (CLAUDE.md acknowledges this). Start with the highest-risk seams:
- `parseMarkdown` cases (links, tables, placeholder survival) once it's a lib, or before
- `ChatService` message building: RAG context injection, thinking-block text extraction,
  temperature guard per model family
- `schemas/bot.py` max-tokens validation per model
- One end-to-end chat test per provider with the API mocked

## 5. Model catalog maintenance
`MODEL_MAX_TOKENS` (schemas/bot.py) and `_model_accepts_temperature`
(chat_service.py) are hand-maintained; every new model family needs a code change
(Claude 5 family added 2026-07-28). Options: query the Models API
(`client.models.retrieve(id)` exposes `max_tokens` and capabilities) at startup with the
static dict as fallback, or just accept the manual step — but write it down in CLAUDE.md
as a launch-day checklist item.

## 6. Dependency cadence
`anthropic==0.71.0` works but trails the SDK. Bump `anthropic`, `openai`,
`qdrant-client`, and `fastapi` quarterly-ish; the pinned-requirements + Railway setup
makes this low-risk. (Contrast: Flowise died of exactly this — its Sept 2025 build no
longer compiles at all.)

## 7. Deploy noise
`railway up` spawns two build attempts, one of which reports FAILED and emails Sage even
when the sibling succeeds. Investigate (Railway support / config) or note it in CLAUDE.md
so failure emails get checked against `railway deployment list` before anyone panics.

## Explicit non-goals
Multi-tenant auth, customer signups, billing. If the platform ever needs those, that's a
project decision, not a punch-list item.
