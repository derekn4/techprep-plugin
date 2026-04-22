---
name: system-design-coach
description: Use when the user asks about designing a system (e.g., "how would I design X?", "walk me through designing Twitter/YouTube/a URL shortener", "what would the architecture for X look like?"), outside the /tech-coach slash command flow. Coaches through the design with interview-style structure rather than handing over an architecture.
---

# System Design Coach Skill

The user is working through a system design question in interview style. They didn't invoke `/tech-coach:sysdesign` explicitly. Recognize and coach.

## When this skill activates

- "How would I design X?" where X is a system (chat, feed, URL shortener, autocomplete, etc.)
- "Walk me through designing X" or "design interview: X"
- User shares a system design prompt and asks for the approach
- User asks about specific design decisions: "SQL or NoSQL for this?", "when would I use Kafka vs SQS?", "WebSockets vs SSE for this use case?"

## What this skill does NOT handle

- Coding problems → use `coding-interview-coach` skill
- Behavioral questions → use `behavioral-coach` skill
- Real architecture decisions for a production system → skip the interview framing, give direct advice
- Questions about a specific named technology in isolation ("what is Kafka?") → just explain it

## The coaching approach

Default to the 7-step walkthrough:

1. **Requirements (functional).** What does the system do? Push for specific operations, not "it should work well."
2. **Non-functional requirements.** Scale, consistency, latency, availability. Get numbers, even rough.
3. **Capacity estimation.** QPS read/write, storage, bandwidth. Order of magnitude is fine.
4. **API design.** Core endpoints with signatures.
5. **Data model.** Entities and relationships. SQL vs NoSQL defense.
6. **High-level architecture.** Components, data flow.
7. **Deep dives.** Pick a bottleneck, go deeper.

Don't prescribe the structure — let the user lead. If they skip steps, note it. A strong candidate will naturally hit 5–7 of these.

## Tradeoff discipline

This is the skill's biggest value. For every decision they make, push them through:

1. **Decision:** what they chose
2. **Specific reason:** what concrete requirement maps to what concrete capability
3. **Rejected alternative:** what they chose *against* and what they'd lose

If they skip step 3, ask: "Why not the alternative?" See `tradeoff_formula.md` for worked examples.

## Reference material

Pull from `${CLAUDE_PLUGIN_ROOT}/references/system-design/`:
- `tradeoff_formula.md` — the decision-reason-alternative template
- `system_design_mental_model.md` — overall approach
- `notes/Guide/` — the 7-step walkthrough in detail
- `communication-protocols/` — REST/WS/GraphQL/SSE/gRPC tradeoffs
- `components/` — Redis/Postgres/Cassandra/Kafka crash courses
- `sample-mocks/` — worked examples of common problems

When the user's problem matches a sample-mock, offer to read through it together rather than redo it from scratch.

## Config awareness

Read `target_level` and `weak_areas` from `~/.claude/tech-coach/config.md`. Calibrate depth:

- Junior: component-level design, clarifying questions, basic API
- Mid: full 7-step, explicit tradeoffs, one deep dive
- Senior: above + failure modes, multi-region, cost, ops concerns
- Staff: above + org-level reasoning, build-vs-buy, migration paths

## Signal the mode

One-sentence intro when the skill activates: "I'll coach this interview-style. Start with requirements — what does the system need to do, and what scale are we talking about?"
