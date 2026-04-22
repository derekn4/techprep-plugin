# prep_summary

This folder holds daily prep summary notes, one file per day. Each `/tech-coach` session ends by writing one.

## How to write a summary

File name: `YYYY-MM-DD.md` (today's date). If a file for today already exists, append a new section to it rather than overwriting — a single day can have multiple sessions.

## Structure

```markdown
# Prep summary — YYYY-MM-DD

## Session N — HH:MM (session type)

**Covered:**
- (what topics / problems / stories)

**Went well:**
- (specific things — "articulated the DP recurrence before coding", not "did well")

**Weak / to practice:**
- (specific things — "missed the base case until prompted", not "need more practice")

**Next focus:**
- (one concrete thing to work on next session)

**Config/status updates:**
- (any changes made to ~/.claude/tech-coach/config.md or ./current-status.md)
```

## Why this exists

- Tracks progress across days and catches repeating weak spots.
- Gives the coach context on what you've already covered (read the last few summaries at session start).
- Produces a log you can share with a mentor or reference before a real interview.

The `Stop` hook in this plugin blocks any `/tech-coach` session from ending without a summary file. If you see the hook nag you, that's working as designed — write the summary before moving on.
