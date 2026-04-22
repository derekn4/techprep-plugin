#!/usr/bin/env python3
"""
UserPromptSubmit hook for /tech-coach commands.

Injects:
  1. Current date + day of week
  2. Contents of the user's config at ~/.claude/tech-coach/config.md (if present)
  3. Days-to-interview countdown (if next_interview: is set in the config)

Silent no-op for prompts that don't invoke /tech-coach.
"""

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path


def main() -> int:
    prompt = os.environ.get("CLAUDE_USER_PROMPT", "")
    if not _is_tech_coach_prompt(prompt):
        return 0

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
        lines.append(f"- Config: MISSING at `{config_path}` — on first `/tech-coach` invocation, copy `templates/config.md` from this plugin to that path and prompt the user to fill it in.")

    print("\n".join(lines))
    return 0


def _is_tech_coach_prompt(prompt: str) -> bool:
    """Only fire for prompts that actually invoke /tech-coach (anchored to avoid over-match)."""
    stripped = prompt.lstrip()
    return stripped.startswith("/tech-coach")


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
