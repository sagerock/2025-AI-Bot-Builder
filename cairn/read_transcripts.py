"""Read / export Cairn conversation transcripts from the bot builder.

Pulls conversations and their full messages via the admin analytics API
(the DB itself is only reachable from inside Railway, so we go through the
authenticated HTTP API instead).

Auth: logs in as admin using the password from --password or the
ADMIN_PASSWORD env var (so `railway run python cairn/read_transcripts.py`
works with no flags, since Railway injects ADMIN_PASSWORD).

Usage:
    railway run python cairn/read_transcripts.py                  # last 20, to stdout
    python cairn/read_transcripts.py --password 'xxx' --limit 50
    railway run python cairn/read_transcripts.py --out transcripts.md
    railway run python cairn/read_transcripts.py --conversation <id>
"""
import argparse
import json
import os
import sys
import urllib.request

DEFAULT_BASE = "https://aibots.sagerock.com"
CAIRN_BOT_ID = "48a9250d-fe83-4e66-a48f-1f65b14323e5"


def _req(url, cookie=None, data=None):
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = f"session_token={cookie}"
    req = urllib.request.Request(url, data=data, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=60))


def login(base, password):
    body = json.dumps({"username": "admin", "password": password}).encode()
    req = urllib.request.Request(f"{base}/auth/login", data=body,
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30)
    cookie = resp.headers.get("Set-Cookie", "")
    if "session_token=" not in cookie:
        raise SystemExit("Login failed: no session cookie returned (check password).")
    return cookie.split("session_token=")[1].split(";")[0]


def format_transcript(convo):
    lines = [
        f"## Conversation {convo['conversation_id'][:8]}",
        f"_session {convo.get('session_id','?')[:12]} · started {convo.get('started_at','?')}_",
        "",
    ]
    for m in convo.get("messages", []):
        who = "Visitor" if m["role"] == "user" else "Cairn"
        ts = (m.get("created_at") or "")[11:19]
        lines.append(f"**{who}** ({ts}): {m['content']}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Read/export Cairn transcripts")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--bot-id", default=CAIRN_BOT_ID)
    ap.add_argument("--limit", type=int, default=20, help="How many recent conversations")
    ap.add_argument("--conversation", help="Fetch one conversation by id instead of the recent list")
    ap.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"),
                    help="Admin password (or set ADMIN_PASSWORD env)")
    ap.add_argument("--out", help="Write to this Markdown file instead of stdout")
    args = ap.parse_args()

    if not args.password:
        raise SystemExit("No admin password. Pass --password or set ADMIN_PASSWORD "
                         "(tip: run via `railway run`).")

    base = args.base_url.rstrip("/")
    cookie = login(base, args.password)

    if args.conversation:
        ids = [args.conversation]
    else:
        convos = _req(f"{base}/api/analytics/bots/{args.bot_id}/conversations?limit={args.limit}", cookie)
        ids = [c["conversation_id"] for c in convos]
        print(f"Found {len(ids)} conversations.", file=sys.stderr)

    blocks = []
    for cid in ids:
        convo = _req(f"{base}/api/analytics/conversations/{cid}/messages", cookie)
        blocks.append(format_transcript(convo))

    output = ("# Cairn transcripts\n\n" + "\n---\n\n".join(blocks)) if blocks else "No conversations."

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Wrote {len(blocks)} transcript(s) to {args.out}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
