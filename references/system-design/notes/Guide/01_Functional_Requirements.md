# Step 1: Functional Requirements - ACTORS

> **Goal:** Understand what the system does. ~2 minutes.

---

## The Checklist

- **A** - Actions (what are the core operations? CRUD, increment, send, search?)
- **C** - Constraints (limits, deduplication, ordering, permissions, uniqueness?)
- **T** - Triggers (who/what initiates? end user, internal service, scheduled timer?)
- **O** - Output (what does the caller get back? response format, pagination?)
- **R** - Recovery (what happens on failure? retries, cancellation, editing?)
- **S** - State (can callers query status or history? what states exist?)

---

## Target: 3-4 Clarifying Questions, Prioritize A, C, R

- **Actions** (1 question): "What are the core operations?" - this is mandatory, always ask.
- **Constraints** (1-2 questions): "Any ordering, dedup, rate limits, permissions?" - this shapes the design.
- **Recovery** (1 question): "What happens on failure? Do we need retries or idempotency?" - shows you think beyond the happy path.
- Skip T, O, S unless they're non-obvious. Triggers and Output are usually clear from context. State comes up naturally when you design the DB.

---

## Flow in Interview

"Here's what the system does (A), here are the rules (C), here's who calls it (T), here's what they get back (O), here's what happens when things break (R), and here's how they check on it (S)."

You don't need all 6 every time. A simple read-heavy system (URL shortener) might skip Recovery and State. A complex async system (task scheduler) hits all 6. Start with Actions and Constraints - those two shape the design the most.
