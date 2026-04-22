# tech-coach config

Fill this in. Every `/tech-coach` subcommand reads this file and adapts. Keep it at `~/.claude/tech-coach/config.md` (the location is auto-created on first run).

## Level

Your current level and the level you're interviewing for. Drives calibration — the coaching gets stricter as the target level climbs.

- `current_level`: junior | mid | senior | staff
- `target_level`: junior | mid | senior | staff

## Interview target

Anything here is optional but the more you fill in, the more specific the coaching gets.

- `target_company`: (company name, or leave blank)
- `target_role`: (e.g., "SWE III", "iOS Engineer", "Backend Engineer")
- `next_interview`: YYYY-MM-DD (or leave blank if no date yet — hook will skip the countdown)
- `interview_format`: (e.g., "4 rounds: 2 coding + 1 sysdesign + 1 behavioral", or leave blank)

## Coding

- `preferred_language`: python | typescript | java | cpp | go | swift | ...
- `strong_areas`: list topics where you're solid (arrays, trees, graphs, DP, etc.)
- `weak_areas`: list topics to prioritize (dynamic programming, concurrency, sysdesign scale estimates, etc.)

## Behavioral

- `have_stories_for`: list behavioral themes you already have STAR stories for (conflict, ownership, failure, leadership, etc.)
- `needs_stories_for`: list themes you need to develop stories for

## Notes

Free text. Anything you want the coach to remember across sessions — cooldown dates, recruiter names, prior feedback, what you're working on at your day job.

```
notes: |
  (your notes here)
```

---

**Example filled-in config:**

```yaml
current_level: mid
target_level: senior
target_company: Google
target_role: SWE III
next_interview: 2026-05-20
interview_format: Round 1 virtual (coding + behavioral), Round 2 onsite (2x coding)
preferred_language: python
strong_areas:
  - trees and graphs
  - concurrency basics
weak_areas:
  - dynamic programming
  - system design scale estimates
  - WebSocket tradeoffs
have_stories_for:
  - conflict
  - ownership
needs_stories_for:
  - failure
  - cross-team influence
notes: |
  Prior feedback: ask more clarifying questions, more structure,
  own the discussion. Working on composure under time pressure.
```
