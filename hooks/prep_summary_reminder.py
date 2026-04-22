#!/usr/bin/env python3
"""
Stop hook for /tech-coach sessions.

Blocks the turn from ending when:
  1. The current session invoked /tech-coach (a session marker exists), AND
  2. `./prep_summary/YYYY-MM-DD.md` does not exist in the session's cwd.

Returns JSON {"decision": "block", "reason": "..."} to force Claude to
continue the turn and write the summary before stopping.

Silent no-op if no session marker (this session didn't use /tech-coach)
or if today's summary already exists.

The marker is cleared once the summary is written, so re-running with the
summary present exits cleanly.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

SESSION_MARKERS_DIR = Path.home() / ".claude" / "tech-coach" / "session-markers"


def main() -> int:
    stdin_data = _read_stdin_json()
    session_id = str(stdin_data.get("session_id") or "unknown")

    marker = SESSION_MARKERS_DIR / f"{session_id}.marker"
    if not marker.exists():
        # This session didn't invoke /tech-coach. No enforcement.
        return 0

    cwd = _read_marker_cwd(marker) or stdin_data.get("cwd") or os.getcwd()
    prep_dir = Path(cwd) / "prep_summary"
    today_file = prep_dir / f"{date.today().isoformat()}.md"

    if today_file.exists():
        # Summary written — clear the marker so future Stop events pass silently.
        try:
            marker.unlink()
        except Exception:
            pass
        return 0

    # Block the turn and instruct Claude to write the summary.
    reason = (
        f"This session used /tech-coach. Before ending the turn, write a prep "
        f"summary at `{today_file}` following the structure in `prep_summary/CLAUDE.md` "
        f"(or the plugin template `templates/prep-summary-CLAUDE.md` if the project "
        f"hasn't been set up with `/tech-coach:init` yet). Cover: what was worked on, "
        f"what went well, what was weak, and one concrete thing to practice next. "
        f"Also ask the user whether `current-status.md` needs updates."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def _read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def _read_marker_cwd(marker: Path) -> str | None:
    try:
        return marker.read_text(encoding="utf-8").strip() or None
    except Exception:
        return None


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Never hang the session on hook failure — fail silently to stderr.
        print(f"[tech-coach prep_summary_reminder] non-fatal: {exc}", file=sys.stderr)
        sys.exit(0)
