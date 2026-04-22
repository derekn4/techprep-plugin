# System Design Interview Flow - Mid-Level SWE Guide

> **How to use this guide:** Follow steps 01-07 in order. Each file covers one phase of the interview. The whole interview is ~45 minutes.

---

## Interview Flow Summary

| Phase | File | Acronym | What you're doing | Time |
|---|---|---|---|---|
| 1. Functional Reqs | `01` | **ACTORS** | What does the system do? | ~2 min |
| 2. Non-Functional Reqs | `02` | **SCALED** | How well does it need to do it? | ~2 min |
| 3. Capacity Estimation | `03` | **Traffic → Storage → Bandwidth → Memory** | How big is it? What does scale imply? | ~3 min |
| 4. API Design | `04` | **ROPES** | How do clients talk to it? | ~3 min |
| 5. Database Design | `05` | **TABLE** | How is data stored and queried? | ~5 min |
| 6. High-Level Architecture | `06` | *(skeletons)* | How do the boxes connect? | ~15 min |
| 7. Deep Dive | `07` (reference) | *(interviewer picks)* | Prove depth on one area | ~10 min |

**Total clarification (phases 1-3): ~7 minutes.** Then you're designing.

**Clarification budget for a typical interview round: ~6 questions total.**
- Functional (ACTORS): 3-4 questions, prioritize A, C, R
- Non-Functional (SCALED): 2-3 questions, prioritize S, C
- Capacity: 0 questions -- state assumptions, let interviewer correct you
