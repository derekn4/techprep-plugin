---
description: Synthesize trends across prep summaries — session counts, topic distribution, mock trajectory, recurring weak spots, proposed config updates.
---

# /tech-coach:progress

Reads the user's `prep_summary/*.md` files in the current working directory and produces a synthesis report. Turns a pile of dated summaries into a signal about where their prep is actually going.

## Usage

- `/tech-coach:progress` — default, last 30 days
- `/tech-coach:progress 7` — last N days (accepts any integer)
- `/tech-coach:progress all` — every summary file in `prep_summary/`

If the user invokes with no argument, assume 30 days.

## Step 1 — Gather summaries

Read every `prep_summary/YYYY-MM-DD.md` file in the current project that falls within the requested window. Today's date comes from the injection hook. If `prep_summary/` doesn't exist or is empty, tell the user:

> "No prep summaries found in `./prep_summary/`. Run `/tech-coach:init` to set up, or start a session — summaries appear after each completed unit."

Don't proceed if there's nothing to synthesize.

## Step 2 — Parse each summary

Each file follows the structure in `${CLAUDE_PLUGIN_ROOT}/templates/prep-summary-CLAUDE.md`. Extract every block:

- **Problem / Design / Story / Mock blocks**: pull the type, time, pattern/theme tag, problem title, "Went well", "Weak", "Next focus"
- **Session wrap blocks**: pull the synthesis line + any "Config updates" line

Track:
- Block count by type (coding problems / sysdesign walkthroughs / stories / mocks)
- Pattern/topic tags from block headers (e.g., "DP", "BFS", "ownership", "URL shortener")
- Mock ratings in order (HIRE / LEAN HIRE / LEAN NO HIRE / NO HIRE) with dates
- All "Weak" entries across all blocks (for recurrence analysis)
- All "Went well" entries (for strengths analysis)
- Behavioral story titles (to see which stories the user has exercised)
- Any config changes noted in Session wrap blocks

## Step 3 — Synthesize and report

Output in this structure. Skip sections that have no data.

```
# Progress report — <window, e.g., "last 30 days" or "last 14 days" or "all time">

Covering YYYY-MM-DD to YYYY-MM-DD, N session-days with activity.

## Session breakdown
- Coding problems:    N   (N% of activity)
- Sysdesign designs:  N   (N%)
- Behavioral stories: N   (N%)
- Mock rounds:        N   (N%)

## Topic distribution
- DP:                 N problems
- BFS/DFS:            N problems
- <other patterns>:   N

If skewed (e.g., 80%+ on one pattern), call it out:
"Heavy on DP this window — N of M problems. Broaden next session?"

Or if sparse:
"Only 2 behavioral stories across this window — consider drilling one of the
themes in `needs_stories_for`."

## Mock interview trajectory
YYYY-MM-DD  LEAN NO HIRE  (coding, LIS)
YYYY-MM-DD  LEAN HIRE     (coding, LRU cache)
YYYY-MM-DD  HIRE          (behavioral)

Pattern observation: "Ratings trending up — 3 mocks, last 2 at LEAN HIRE+"
Or:                   "Ratings flat — 4 mocks, all LEAN NO HIRE on weak-area
                       problems. Time to drill before the next mock."

## Recurring weak spots
Group similar "Weak" entries by fuzzy match. Show the top 3-5 themes with frequency:

- "Missed / late on edge cases"                    appeared 7 times
- "Couldn't defend DB choice"                      appeared 4 times
- "Stuck on DP recurrence without prompting"       appeared 3 times

These are the honest candidates for `weak_areas` in config. Propose them
if they're not already there:
"`<specific phrase>` shows up N times but isn't in `weak_areas` yet.
Add? (yes/no/rephrase)"

## Strengths (what's consistently working)
- "Clean complexity analysis"                      appeared 6 times
- "Good clarifying questions"                      appeared 5 times

If any of these correspond to topics currently in `weak_areas`, propose promotion:
"You listed 'DP' as a weak area, but you've hit 4 DP problems strongly in this
window. Move 'DP' from `weak_areas` to `strong_areas`? (yes/no)"

## Behavioral story inventory
List every story title encountered, grouped by theme.

Conflict:
  - "Shipping the migration without a PM"   practiced 3x, last 8 days ago
Ownership:
  - "Refactoring the auth layer"             practiced 1x, 21 days ago
Failure:  (no stories in this window)

If themes from `needs_stories_for` have no stories in this window:
"`needs_stories_for: [failure, leadership]` — no stories on either in the
last N days. Drill one next session?"

If a story hasn't been touched in 14+ days:
"Story 'X' — last practiced 21 days ago. Rust risk; consider a refresh."

## Suggested next focus (one line)

Based on everything above, pick ONE thing to prioritize next session. Be
specific. Not "practice more DP" — "drill the DP + binary-search optimization
pattern (weak on 3 problems this window)."
```

## Step 4 — Propose confirmed config updates

After presenting the report, propose specific config updates based on patterns. Don't auto-write. Ask for confirmation on each, in order:

1. New weak areas (from recurring weak spots)
2. Promotions weak → strong (from consistently-strong areas that were flagged weak)
3. Behavioral inventory updates (`have_stories_for` / `needs_stories_for` based on practiced/unpracticed themes)

Edit `~/.claude/tech-coach/config.md` once the user confirms each batch. Note changes in today's prep summary under a Session wrap block (or create one if today has no sessions).

## Notes

- **No silent writes.** Every config change is proposed and confirmed.
- **Honest signal over flattery.** If the user has been cruising on easy problems, say it: "12 mediums, 0 hards. Next-level problems are harder for a reason — try one."
- **Fuzzy-match weak spots carefully.** "Missed base case" and "forgot the base case" and "didn't handle the empty input" are all the same theme. Collapse similar phrasings when counting. But don't collapse too aggressively — "DP base case" and "recursion base case" are related but distinct.
- **Report is the artifact.** The user may want to save or share it. Offer: "Save this as `prep_summary/progress-YYYY-MM-DD.md`?" at the end.
- **No session wrap here.** This command is a meta-report; it doesn't trigger the standard per-unit / session-wrap flow. The Stop hook will still enforce *today's* summary exists — since you may edit it with config changes, that should be fine.
