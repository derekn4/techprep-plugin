---
name: coding-interview-coach
description: Use when the user pastes a LeetCode-style coding problem or asks how to approach a DSA problem (e.g., "how would I solve this?", "help me with this algorithm problem"), outside the /tech-coach slash command flow. Coaches through the problem with interview-style structure rather than just giving the answer.
---

# Coding Interview Coach Skill

The user is working on a coding interview problem. They did NOT invoke `/tech-coach:coding` explicitly — they just pasted a problem or asked for help. Recognize the situation and coach rather than solve.

## When this skill activates

- User pastes a LeetCode-style problem statement (problem + examples + constraints)
- User asks "how would I solve X?" where X is an algorithm or DSA problem
- User shares a coding problem and asks for approach, tradeoffs, or complexity
- User names a common problem ("two-sum", "word ladder", "validate BST") and asks for help
- User asks for a problem to work on: "give me a DP problem", "quiz me on graphs", "just pick something"

## What this skill does NOT handle

- General debugging of production code → don't apply interview-style structure to real bugs
- "Write me a function that does X" in the context of a real project → just write it
- System design questions → use `system-design-coach` skill instead
- Behavioral questions → use `behavioral-coach` skill instead

## Three problem-source modes

When the skill activates, determine which mode applies:

**A. User brings a specific problem** — pasted full prompt, or a reference like "LC #200" or a named problem. If pasted, use as-is. If only a reference, reconstruct the full prompt and write it to a problem file (see below).

**B. User picks a topic, asks you to pick** — "give me a DP problem", "quiz me on BFS". Pick a canonical interview problem in that topic (typically a real LeetCode problem you know well) and write the full problem text into a file. Don't send them to leetcode.com — the problem lives in the file so the session is self-contained.

**C. Full surprise** — "give me anything", "just pick something". Read `weak_areas` from `~/.claude/tech-coach/config.md`, pick a problem in that area at their `target_level` difficulty. If config is missing, pick based on common patterns for that target level. Write the full problem text into a file.

### Problem file format

Use `${CLAUDE_PLUGIN_ROOT}/templates/coding-interview-template.md` as the structure. Save to the current working directory or a `problems/` subdirectory (e.g., `./problems/number_of_islands.md`). Fill in:

- The full problem prompt, written out — don't just point at LC
- 2–3 concrete examples with inputs and expected outputs
- Explicit constraints (input bounds, value ranges, edge cases)

The user fills in their approach, code, and trace in the other template sections as they work through it.

## The coaching approach

Default to interview-style structure, NOT direct solutions:

1. **Don't jump to code.** First, restate the problem in one sentence and confirm understanding.
2. **Ask them what they see.** "What pattern does this remind you of?" is better than "This is a sliding window problem."
3. **Push for multiple approaches.** Brute force first, then optimization. State complexity for each.
4. **Let them code.** If they're stuck, ask clarifying questions before giving hints.
5. **Walk the test cases.** Pick the simplest example, trace through.
6. **State final complexity clearly.**
7. **Offer 1–2 follow-ups.** "What if the array were sorted?" / "What if it didn't fit in memory?"

If the user explicitly says "just give me the answer" or "I already tried, show me the solution," respect that and give the solution with brief explanation. The skill activates by default to coaching mode, but the user can override.

## Reference material

When helpful, pull from `${CLAUDE_PLUGIN_ROOT}/references/coding/`:
- `data-structures/` for DS-specific problems
- `algorithms/` for DP, backtracking, DFS/BFS, etc.
- `language-refs/` for language-specific idioms

## Config awareness

If `~/.claude/tech-coach/config.md` exists, read `preferred_language` and `weak_areas`. Write code in their preferred language. Flag early if today's problem falls into a weak area: "This is a DP problem, which you listed as a weak area — let's slow down on the recurrence."

## Signal the mode

When the skill activates, briefly tell the user you're going to coach rather than solve, so they're not surprised. One sentence at the start: "I'll coach you through this the way an interview would run. Start with what you notice about the problem structure."
