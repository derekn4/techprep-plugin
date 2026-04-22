#!/usr/bin/env python3
"""
UserPromptSubmit hook for /tech-coach commands.

Injects:
  1. Current date + day of week
  2. Contents of the user's config at ~/.claude/tech-coach/config.md (if present)
  3. Days-to-interview countdown (if next_interview: is set in the config)

Also writes a per-session marker file so the Stop hook knows this session
invoked /tech-coach and should enforce the prep_summary requirement.

Silent no-op for prompts that don't invoke /tech-coach.
"""

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

SESSION_MARKERS_DIR = Path.home() / ".claude" / "tech-coach" / "session-markers"


def main() -> int:
    stdin_data = _read_stdin_json()
    prompt = _get_prompt(stdin_data)
    if not _is_tech_coach_prompt(prompt):
        return 0

    _write_session_marker(stdin_data)

    today = date.today()
    lines = [
        "## tech-coach context",
        f"- Today: {today.isoformat()} ({today.strftime('%A')})",
    ]

    config_path = Path.home() / ".claude" / "tech-coach" / "config.md"
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8", errors="replace")
        lines.append(f"- Config: `{config_path}`")

        countdown = _days_to_interview(config_text, today)
        if countdown is not None:
            lines.append(f"- Days to interview: {countdown}")

        lines.append("")
        lines.append("### Current config")
        lines.append("```")
        lines.append(config_text.strip())
        lines.append("```")
    else:
        lines.append(
            f"- Config: MISSING at `{config_path}` — suggest `/tech-coach:init` to create it from the plugin template."
        )

    print("\n".join(lines))
    return 0


def _read_stdin_json() -> dict:
    """Read JSON payload from stdin if available. Empty dict on any failure."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def _get_prompt(stdin_data: dict) -> str:
    """Prefer stdin JSON (modern hook interface), fall back to env var."""
    prompt = stdin_data.get("prompt") or stdin_data.get("user_prompt")
    if prompt:
        return str(prompt)
    return os.environ.get("CLAUDE_USER_PROMPT", "")


def _is_tech_coach_prompt(prompt: str) -> bool:
    """Only fire for prompts that actually invoke /tech-coach."""
    stripped = prompt.lstrip()
    return stripped.startswith("/tech-coach")


def _write_session_marker(stdin_data: dict) -> None:
    """
    Write a per-session marker file. The Stop hook reads this to know the
    current session invoked /tech-coach and must produce a prep summary.

    Marker contents: the cwd where the session is running, so the Stop hook
    can check for `./prep_summary/YYYY-MM-DD.md` at the right path.
    """
    session_id = str(stdin_data.get("session_id") or "unknown")
    cwd = stdin_data.get("cwd") or os.getcwd()
    try:
        SESSION_MARKERS_DIR.mkdir(parents=True, exist_ok=True)
        marker = SESSION_MARKERS_DIR / f"{session_id}.marker"
        marker.write_text(str(cwd), encoding="utf-8")
    except Exception as exc:
        # Never let marker-write failure block the user's prompt.
        print(f"[tech-coach inject_context] marker write failed: {exc}", file=sys.stderr)


def _days_to_interview(config_text: str, today: date) -> int | None:
    """Parse `next_interview: YYYY-MM-DD` from the config. Return days until, or None."""
    match = re.search(
        r"^\s*[-*]?\s*`?next_interview`?\s*:\s*(\d{4}-\d{2}-\d{2})",
        config_text,
        re.MULTILINE,
    )
    if not match:
        return None
    try:
        target = datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None
    return (target - today).days


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Never block the user's prompt on a hook failure — fail silently to stderr.
        print(f"[tech-coach inject_context] non-fatal: {exc}", file=sys.stderr)
        sys.exit(0)
