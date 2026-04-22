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

## Step 5 — Write the prep summary

After the evaluation is shown, prompt the user with two questions:

1. "Want to update your config based on this eval? (e.g., new weak area to add, or moving something from `needs_stories_for` to `have_stories_for`)"
2. "Does `current-status.md` need updates? (e.g., mock round completed, upcoming real interview shifted)"

Then write `prep_summary/YYYY-MM-DD.md` covering:

- Mock round type and the problem
- Evaluation rating + one-sentence reason
- Top 1–2 things the evaluation flagged to practice next
- Any config or status changes made

The `Stop` hook will block without a summary.

## Notes

- **One mock per session.** A full round is cognitively demanding. Don't run two back-to-back — schedule the second for another day.
- **Budget the time.** If the user has 20 minutes, DON'T run a full mock. Run `/tech-coach:coding` or a focused drill instead. Mocks need the full ~45 minutes to be useful.
- **Save evaluations.** The evaluation text is the whole point. Make sure it lands in the prep summary so the user can track ratings across mocks over time.
