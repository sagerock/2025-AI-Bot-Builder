"""Run scripted conversation evals against a deployed Cairn bot.

Usage:
    python cairn/run_evals.py --base-url https://<bot-builder>.up.railway.app --bot-id <cairn-bot-id>

Reads each YAML in cairn/evals/, runs the scripted turns against the bot's
/api/chat/<bot_id> endpoint, and checks the assertions in `expect`. Prints
a summary at the end. Exits non-zero if any eval fails.

This is intentionally lightweight: no LLM-as-judge, just simple substring and
tool-call checks. It catches obvious regressions without being expensive.
"""
import argparse
import sys
import uuid
from pathlib import Path

import httpx
import yaml

EVALS_DIR = Path(__file__).resolve().parent / "evals"


def check_expectations(response_text: str, tools_called: list[str], expect: dict) -> list[str]:
    """Return a list of failure messages. Empty list = passed."""
    failures = []
    lower = response_text.lower()

    if "response_contains_any" in expect:
        targets = [t.lower() for t in expect["response_contains_any"]]
        if not any(t in lower for t in targets):
            failures.append(f"none of {expect['response_contains_any']} in response")

    if "response_does_not_contain_any" in expect:
        for token in expect["response_does_not_contain_any"]:
            if token.lower() in lower:
                failures.append(f"response contains forbidden token {token!r}")

    if "tools_called_any" in expect:
        target_tools = set(expect["tools_called_any"])
        if not target_tools.intersection(set(tools_called)):
            failures.append(f"none of tools {target_tools} called (saw {tools_called})")

    return failures


def run_one_eval(base_url: str, bot_id: str, eval_path: Path) -> tuple[str, list[str]]:
    """Run one eval; return (name, list of failures)."""
    with open(eval_path) as f:
        eval_data = yaml.safe_load(f)

    name = eval_data["name"]
    session_id = f"eval-{name}-{uuid.uuid4().hex[:8]}"
    all_failures = []

    with httpx.Client(timeout=120.0) as client:
        for i, turn in enumerate(eval_data["turns"]):
            user_message = turn["user"]
            expect = turn.get("expect", {})

            # Bot builder's chat endpoint uses Form() params, not JSON.
            response = client.post(
                f"{base_url}/api/chat/{bot_id}",
                data={"message": user_message, "session_id": session_id},
            )
            if response.status_code != 200:
                all_failures.append(f"turn {i+1}: HTTP {response.status_code} - {response.text[:200]}")
                break

            data = response.json()
            response_text = data.get("response", "") or data.get("message", "")
            tools_called = data.get("tools_called", []) or []

            failures = check_expectations(response_text, tools_called, expect)
            if failures:
                all_failures.extend(f"turn {i+1}: {f}" for f in failures)

    return name, all_failures


def main():
    parser = argparse.ArgumentParser(description="Run Cairn conversation evals")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--bot-id", required=True)
    parser.add_argument("--only", help="Run only one eval by name (filename stem)")
    args = parser.parse_args()

    eval_files = sorted(EVALS_DIR.glob("*.yaml"))
    if args.only:
        eval_files = [p for p in eval_files if p.stem == args.only]
        if not eval_files:
            print(f"No eval matching --only {args.only!r}")
            sys.exit(2)

    print(f"Running {len(eval_files)} evals against {args.base_url}/api/chat/{args.bot_id}\n")
    summary = []
    for eval_path in eval_files:
        print(f"  {eval_path.stem}... ", end="", flush=True)
        name, failures = run_one_eval(args.base_url, args.bot_id, eval_path)
        if failures:
            print("FAIL")
            for f in failures:
                print(f"    - {f}")
            summary.append((name, False))
        else:
            print("OK")
            summary.append((name, True))

    passed = sum(1 for _, ok in summary if ok)
    total = len(summary)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
