---
description: Run a full mock interview round (coding / system design / behavioral) via the mock-interviewer agent.
---

# /tech-coach:mock

Launches a realistic mock interview round. The actual interview runs in an isolated subagent (`mock-interviewer`) so the role-play doesn't clutter the main conversation. When it finishes, only the structured evaluation comes back.

## Step 1 — Confirm parameters

Read the user's config at `~/.claude/tech-coach/config.md`. You'll need:

- `target_level` — drives problem difficulty and evaluation bar. If missing, ask.
- `preferred_language` — for coding rounds. If missing, ask.
- `weak_areas` — biases which problem to pick (practicing weak spots is the highest-leverage use of a mock).

Then ask the user which round type they want:

```
Which mock round?
  1. Coding
  2. System design
  3. Behavioral
```

If they say "any" or "surprise me," pick one that exercises their weakest area per config.

## Step 2 — Set expectations

Before launching, tell the user what to expect, briefly:

- A full round takes ~45 minutes. You'll be interacting with an interviewer persona who will NOT coach you mid-session — they observe and evaluate at the end.
- Rate yourself honestly. The evaluation is more useful if the interviewer is strict. Err toward below-bar — real interviewers do.
- When the round ends, you'll get a structured evaluation (HIRE / LEAN HIRE / LEAN NO HIRE / NO HIRE) with specific feedback.

Ask them to confirm they're ready.

## Step 3 — Launch the subagent

Invoke the `mock-interviewer` agent. Pass in:

- `round_type` (coding / sysdesign / behavioral)
- `level` (from config's `target_level`)
- `language` (from config's `preferred_language`, for coding rounds only)
- Any `weak_areas` the agent should bias the problem selection toward
- Any `target_company` from config (lets the agent calibrate style — e.g., Amazon-style behavioral questions emphasize Leadership Principles)

The user interacts directly with the subagent. You're out of the loop until it returns.

## Step 4 — Surface the evaluation

When the subagent returns, it will produce a structured evaluation (see the `mock-interviewer.md` agent definition for the exact format). Display it to the user as-is. Don't add your own commentary on top — the evaluation is the artifact.

## Step 5 — Append the mock block to today's prep summary

Append a **Mock** block to `prep_summary/YYYY-MM-DD.md` in the current working directory. See `${CLAUDE_PLUGIN_ROOT}/templates/prep-summary-CLAUDE.md` for the full format.

```markdown
## Mock — HH:MM (<round_type> · <level>)
**Problem:** <title>
**Rating:** HIRE | LEAN HIRE | LEAN NO HIRE | NO HIRE
**One-line reason:** <from the eval>
**What went well:** <top 1–2 from eval>
**What was weak:** <top 1–2 from eval>
**Next focus:** <concrete practice items from eval's "top 3 things to practice next">
```

If today's file doesn't exist yet, create it with a `# Prep summary — YYYY-MM-DD` header.

## Step 6 — Propose specific config updates

Don't ask the vague "want to update your config?" question. Read the eval's weak spots and propose **specific diffs** with user confirmation:

> "The eval flagged [specific weakness]. Propose adding `<specific phrase>` to `weak_areas` in config. Confirm?"

For behavioral mocks, also check:
- Did any story surface as solid? Propose moving its theme from `needs_stories_for` → `have_stories_for`.
- Did any theme come up with no good story? Propose adding to `needs_stories_for`.

For coding/sysdesign mocks, check `weak_areas` and `strong_areas` — propose moves in either direction based on the eval.

If the user confirms, edit `~/.claude/tech-coach/config.md` and note the change in the Mock block under a **Config updates** line.

## Step 7 — Check current-status.md

Ask whether `current-status.md` needs updates (e.g., real interview coming up, recent recruiter contact, feedback received outside the plugin). Edit if so.

The `Stop` hook will block without today's summary file. The Mock block in step 5 satisfies it.

## Notes

- **One mock per session.** A full round is cognitively demanding. Don't run two back-to-back — schedule the second for another day.
- **Budget the time.** If the user has 20 minutes, DON'T run a full mock. Run `/tech-coach:coding` or a focused drill instead. Mocks need the full ~45 minutes to be useful.
- **Save evaluations.** The evaluation text is the whole point. Make sure it lands in the prep summary so the user can track ratings across mocks over time.
