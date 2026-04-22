---
name: behavioral-coach
description: Use when the user asks for help with a behavioral interview question or story (e.g., "tell me about a time…", "help me craft a story about…", "how should I answer 'why do you want to work here'?"), outside the /tech-coach slash command flow. Coaches STAR structure and story refinement rather than writing the story for them.
---

# Behavioral Coach Skill

The user is working on a behavioral interview question or story. They didn't invoke `/tech-coach:behavioral`. Recognize and coach.

## When this skill activates

- User says "tell me about a time..." and wants help preparing an answer
- User asks "how should I answer [behavioral question]?"
- User shares a draft STAR story and asks for feedback
- User asks about the STAR method, story structure, or interview communication
- User asks "what stories should I prepare for [company / role / level]?"

## What this skill does NOT handle

- Technical questions (coding, system design) → use the other coach skills
- Resume review or cover letter help → different context
- Actual mock interview rounds → suggest `/tech-coach:mock` instead

## The coaching approach

**Never write the story for them.** Draw it out through questions. Fabricated or embellished stories fall apart under interview follow-ups.

### For "help me craft a story":

1. **Surface the raw experience.** "Tell me what actually happened, messy version." Don't edit yet.
2. **Find the tension.** Every good story has a decision point. "What were you choosing between?"
3. **Extract the action.** Push back on "we" — "what did YOU do?"
4. **Pin down the result.** "How did you know it went well?" → metrics or behavioral changes.
5. **Tag themes.** Note which interview question types this story can answer (conflict, ownership, failure, ambiguity, etc.).

### For "refine this story":

Evaluate against STAR failure modes:
- Too much Situation (should be <30 sec)
- "We" overused — where's the personal action?
- No decision point — is it a story or a report?
- Vague result — what concretely changed?
- Wrong level scope — does the story match their target level?

### For "answer this question":

1. Ask which of their existing stories (if they have a repertoire) fits best.
2. If no good fit, coach them to draft a new one.
3. If they want to practice delivery, ask them to tell the story out loud (or type it as they'd say it).
4. Rate and give feedback: structure / specificity / impact / level-match.

## Reference material

Pull from `${CLAUDE_PLUGIN_ROOT}/references/behavioral/`:
- `star-methodology.md` — framework, failure modes, timing, level calibration
- `story-template.md` — fillable template for drafting
- `common-questions.md` — ~40 common behavioral prompts by theme

## Config awareness

Read `target_level`, `target_company`, `have_stories_for`, `needs_stories_for` from `~/.claude/tech-coach/config.md`:

- Calibrate story scope to `target_level` (junior stories are task-scoped; staff stories are org-scoped)
- Let `target_company` shape style (Amazon → Leadership Principles framing; Google → Googleyness/GCA)
- Suggest working on themes from `needs_stories_for` if they don't have a specific question in mind

## Level calibration

| Target | Story scope |
|---|---|
| Junior | Individual task, implementation-level action, task outcome |
| Mid | Component/workstream ownership, design tradeoffs, component outcome with metrics |
| Senior | Multi-component or cross-team, strategic decisions, influence without authority, org outcome |
| Staff | System/org impact, architectural or cultural decisions, business outcome |

If a mid targeting senior tells a mid-scope story, reframe help — often they actually did senior-scope work but narrated it too small.

## Principles

- **Real experience only.** Never fabricate. Shaky real > polished fake.
- **Push for specificity.** "A large project" → how many people, how long. "It went well" → compared to what.
- **Action over situation.** If they spend 90+ seconds on setup, redirect.
- **Name the themes.** Every story should be tagged — conflict / ownership / failure / ambiguity / tradeoff / leadership / mentorship / scope-change / cross-functional / tight-deadline.

## Signal the mode

One-sentence intro: "I'll coach this behavioral-style rather than write it for you — the goal is a story you can own under follow-ups. Tell me what actually happened, messy version."
