# prep_summary

This folder holds daily prep summary notes, one file per day. Sessions append to the day's file as they go — a single problem, design, or story finishing triggers an append. At session end, a final synthesis block gets added.

## File name

`YYYY-MM-DD.md` (today's date). A single day's file can contain entries from multiple sessions (morning coding, afternoon behavioral, etc.). Always append — never overwrite.

## Structure

Each discrete unit (one coding problem, one system design walkthrough, one STAR story worked on) gets its own dated block. At the end of each session, a **Session wrap** block synthesizes across the blocks from that session.

```markdown
# Prep summary — YYYY-MM-DD

## Problem 1 — 14:05 (Coding · DP)
**Problem:** Longest Increasing Subsequence (LC #300)
**Went well:** Identified the O(n²) DP recurrence quickly. Clean base case.
**Weak:** Missed the binary-search optimization until prompted.
**Next focus:** Practice "DP + binary search" pattern.

## Problem 2 — 14:35 (Coding · DP)
**Problem:** Partition Equal Subset Sum
**Went well:** Clean subset-sum reduction. Good complexity analysis.
**Weak:** Slow on the space-optimization follow-up.
**Next focus:** 1D rolling-array DP.

## Session wrap — 14:55
Two DP problems in 50 min. Recurring theme: **space optimization is a weak spot**
across both problems. Proposed adding "DP space optimization" to weak_areas in config.

## Story 1 — 19:10 (Behavioral · ownership)
**Story worked on:** "Shipping the migration without a PM"
**What changed:** Refined action section; cut 40 sec of situation; added explicit tradeoff.
**Weak:** Still starting with "we" — need to reframe in first person.
**Next focus:** Re-tell this story in first person only; record and time it.

## Session wrap — 19:35
One behavioral session refining one story. "We vs I" is the theme — flagged for
next session across all stories.
```

### Block types

- **Problem N** — a coding or system design problem
- **Design N** — a system design deep dive (if distinct from a full problem)
- **Story N** — a behavioral story drafted, refined, or mock-practiced
- **Mock** — a full mock round (includes the evaluation rating)
- **Session wrap** — written at the end of each session, synthesizing across that session's blocks

### Fields in each block

- **Problem / Design / Story** — what was worked on (title, ID, theme)
- **Went well** — specific positives ("articulated the DP recurrence before coding", not "did well")
- **Weak** — specific negatives ("missed the base case until prompted", not "need more practice")
- **Next focus** — one concrete thing to practice next (can be same as weak, rephrased as action)

### Config updates

If the coach proposes changes to `~/.claude/tech-coach/config.md` (moving something to `weak_areas`, promoting to `strong_areas`, adding to `needs_stories_for`, etc.), the Session wrap block should note what changed and why:

```markdown
## Session wrap — 14:55
...
**Config updates:** Added "DP space optimization" to weak_areas (flagged on
two problems this session, user confirmed).
```

## Why this exists

- Tracks progress across days and catches repeating weak spots.
- Feeds the `/tech-coach:progress` command to synthesize trends over time.
- Gives the coach context on what you've already covered (read the last few files at session start).
- Produces a log you can share with a mentor or reference before a real interview.

## Stop hook enforcement

The `Stop` hook in this plugin blocks any `/tech-coach` session from ending if today's summary file is missing. Per-unit appending (after each problem/design/story) satisfies this naturally. If you see the hook nag you, write the summary before moving on — don't try to Ctrl-C past it.
