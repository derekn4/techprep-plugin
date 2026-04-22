# techprep-plugin

A Claude Code plugin that coaches you through technical interview prep. Role-agnostic, level-calibrated (junior / mid / senior / staff), and works for any company.

## What it does

Five coaching surfaces, each calibrated to the level you're targeting:

- **`/tech-coach`** — router. Reads your config, asks what today's session is, routes to a subcommand.
- **`/tech-coach:init`** — one-shot setup for a project. Creates `prep_summary/`, `current-status.md`, and the per-user config if missing.
- **`/tech-coach:coding`** — DSA coaching. Bring a problem, ask for one on a topic, or invoke it with nothing for a surprise problem picked from your weak areas.
- **`/tech-coach:sysdesign`** — system design walkthroughs. Full 7-step flow (requirements → non-functional → capacity → API → data → HLD → deep dives) with level-calibrated depth.
- **`/tech-coach:behavioral`** — STAR story coaching. Draft new stories from real experience, refine existing ones, mock-practice delivery, or scan for gaps.
- **`/tech-coach:mock`** — full mock interview round via a dedicated interviewer subagent. Runs in isolation; returns a structured evaluation (HIRE / LEAN HIRE / LEAN NO HIRE / NO HIRE).
- **`/tech-coach:config`** — view or edit your per-user config.

Three auto-activating skills complement the commands — if you paste a coding problem, ask "how would I design X?", or ask "tell me about a time…" in a regular conversation, the right coach kicks in without you needing to type a slash command.

## Install

```
/plugin marketplace add derekn4/techprep-plugin
/plugin install tech-coach@derekn4
```

Then in any project:

```
/tech-coach:init    # first time, sets up config + project files
/tech-coach         # daily, picks a session type
```

## How personalization works

**Per-user config** at `~/.claude/tech-coach/config.md` (one file across all projects):

```yaml
current_level: mid
target_level: senior
target_company: (company name or blank)
target_role: SWE III
next_interview: 2026-05-20
interview_format: Round 1 virtual + Round 2 onsite
preferred_language: python
strong_areas:
  - trees and graphs
  - concurrency basics
weak_areas:
  - dynamic programming
  - system design scale estimates
have_stories_for:
  - conflict
  - ownership
needs_stories_for:
  - failure
  - cross-team influence
```

Every subcommand reads this and adapts — problem difficulty, coaching depth, language examples, story themes to practice. A daily hook injects the current date and days-to-interview countdown so the coach knows where you are in your timeline.

**Per-project files** (one set per project directory where you prep):

- `prep_summary/` — one markdown file per day with per-unit blocks (one per problem/design/story) plus a session wrap. Git-commit if you want prep history in version control.
- `current-status.md` — pipeline tracker. Active applications, past results, recent feedback, current prep focus.

## Prep summaries (how progress tracking works)

After each completed unit (one problem, one design, one story, one mock), the coach appends a block to today's `prep_summary/YYYY-MM-DD.md`. At session end, a **Session wrap** block synthesizes across the units and proposes specific config updates if a pattern emerged.

A `Stop` hook blocks the session from ending without a summary file — incremental appending satisfies this naturally, so you won't usually see the hook fire.

Example of a day's summary:

```markdown
# Prep summary — 2026-04-22

## Problem 1 — 14:05 (Coding · DP)
**Problem:** Longest Increasing Subsequence
**Went well:** Identified the O(n²) DP recurrence quickly.
**Weak:** Missed the binary-search optimization until prompted.
**Next focus:** Practice "DP + binary search" pattern.

## Problem 2 — 14:35 (Coding · DP)
...

## Session wrap — 14:55
Two DP problems, both rough on optimization follow-ups. Proposed adding
"DP space optimization" to weak_areas — confirmed and updated.
```

## Config auto-updates (with confirmation)

The coach never silently edits your config. When it spots a recurring weakness across a session (or a mock evaluation surfaces a specific gap), it proposes a specific diff and asks for confirmation before writing:

> "The coach noticed you struggled with DB-choice justification on both sysdesign walkthroughs today. Add 'sysdesign: DB choice defense' to `weak_areas`? (yes / no / rephrase)"

Symmetric for strengths — if you crush a pattern consistently, the coach proposes moving it from `weak_areas` to `strong_areas`.

## Status

v0.1 — MVP. Role-agnostic coding / system design / behavioral coaching with per-user configuration, level-based calibration, mock interview agent, incremental prep summaries, and session-end config-update proposals.

Post-MVP wishlist: `/tech-coach:progress` for cross-session synthesis, session recovery hook for Ctrl-C resilience, company-specific playbooks (Amazon LPs, Google GCA, Meta values), curated problem bank.

## License

MIT
