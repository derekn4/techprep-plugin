---
description: Set up this project for tech-coach — creates prep_summary/, current-status.md, and the per-user config if missing.
---

# /tech-coach:init

One-shot setup for a project where the user wants to do interview prep. Creates the local files the coach expects and bootstraps the per-user config if it's not already there.

## Step 1 — Check the per-user config

Path: `~/.claude/tech-coach/config.md`.

- **If missing:** create the directory, copy `${CLAUDE_PLUGIN_ROOT}/templates/config.md` to that path, and tell the user: "Config created at `~/.claude/tech-coach/config.md` — fill in at least `current_level`, `target_level`, and `preferred_language` before your next session."
- **If present:** note that it exists, show the current values in a compact summary. Don't overwrite.

## Step 2 — Create `prep_summary/` in the current project

Path: `./prep_summary/` (cwd-relative).

- **If missing:** create the folder and copy `${CLAUDE_PLUGIN_ROOT}/templates/prep-summary-CLAUDE.md` to `./prep_summary/CLAUDE.md`. This tells Claude how to write daily summaries in this project.
- **If present:** check whether `prep_summary/CLAUDE.md` exists; copy it if not.

## Step 3 — Create `current-status.md` in the current project

Path: `./current-status.md`.

- **If missing:** copy `${CLAUDE_PLUGIN_ROOT}/templates/current-status.md` to `./current-status.md`. Tell the user this is their pipeline tracker — what interviews are active, what's next, recent feedback.
- **If present:** leave it alone. Don't overwrite existing user notes.

## Step 4 — Summarize

After setup, print a short block so the user knows what got created:

```
Setup complete.

Files created (or already existed):
- ~/.claude/tech-coach/config.md      <— your level, target, weak areas (edit this)
- ./prep_summary/                      <— daily session summaries land here
- ./prep_summary/CLAUDE.md             <— instructions for Claude on summary format
- ./current-status.md                  <— your interview pipeline (edit this)

Next: run /tech-coach and pick a session type.
```

If any file was skipped (already existed), say which.

## Notes

- Safe to re-run. The command never overwrites existing user content. It only fills in what's missing.
- `prep_summary/` and `current-status.md` live in the current project directory — they stay with the project and can be git-committed if the user wants session history in version control.
- `config.md` is global (per-user across all projects). Changes there carry across every project you prep in.
