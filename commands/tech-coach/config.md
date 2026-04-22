---
description: View or edit the tech-coach per-user config.
---

# /tech-coach:config

Manage the user's tech-coach config at `~/.claude/tech-coach/config.md`.

## If the file does not exist

Copy `templates/config.md` from this plugin to `~/.claude/tech-coach/config.md`, then display its contents and prompt the user to fill in at minimum:
- `current_level`
- `target_level`
- `target_company` (can be blank)
- `next_interview` (can be blank)

## If the file exists

1. Read the file and display the current values in a compact summary:
   ```
   Level: mid → senior
   Target: Google (SWE III)
   Next interview: 2026-05-20 (28 days out)
   Preferred language: python
   Weak areas: dynamic programming, sysdesign scale estimates
   ```

2. Ask what they want to change. Common updates:
   - Interview date moved
   - Level changed (promotion at work, moving to senior prep)
   - New weak area discovered
   - New target company
   - STAR story coverage updated

3. Make the edit. Preserve formatting and comments in the config file. Don't rewrite sections the user didn't ask to change.

4. Show the updated value and confirm.

## Notes

- The config is source of truth. If the user tells you something that should be in config (e.g., "I'm prepping for Amazon now"), update the config, don't just remember it for this session.
- If the user asks "what's my current status" and there's a `current-status.md` in the project, prefer that for recent updates (it's project-local). Config is the durable, cross-project profile.
