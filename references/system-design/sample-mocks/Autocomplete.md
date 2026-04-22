# System Design: Autocomplete / Typeahead Search

**Source:** Common system design interview question

---

## Overview

Design a system that suggests completions as a user types. Think Google search bar, email search, Slack's command palette. The core challenge: **return relevant suggestions in <100ms as the user types each character.**

---

## Clarifying Questions & Answers

| Question | Answer |
|----------|--------|
| What are we autocompleting? (search queries, contacts, emails?) | Assume search queries (most general) |
| How many unique suggestions in the corpus? | ~100 million phrases |
| How many daily active users? | ~50 million |
| How fast must suggestions appear? | <100ms from keystroke to rendered results |
| How many suggestions per query? | Top 5-10 |
| How are suggestions ranked? | By popularity (frequency), recency, personalization |
| Do we need personalized results? | Yes, blend personal history with global popularity |
| Multi-language support? | English first, extensible later |
| Do suggestions update in real-time as new queries come in? | Near-real-time (minutes of delay acceptable) |

---

## Requirements

### Functional
- Given a prefix string, return top K suggestions ranked by relevance
- Suggestions update as user types each character
- Blend personalized results with globally popular ones
- Support deletion of inappropriate/offensive suggestions

### Non-Functional
- **Low latency:** <100ms p99 response time
- **High availability:** Always return something (degrade gracefully)
- **Scalability:** Handle 50M DAU, each typing multiple queries
- **Freshness:** New trending queries appear within minutes
- **Relevance:** Results feel useful, not random

---

## High-Level Design

```
                                         QUERY PATH (real-time)
                                         ─────────────────────

 ┌──────────┐    ┌──────┐    ┌───────────────┐    ┌────────────────────┐
 │  Client   │──►│  LB  │──►│  API Gateway   │──►│ Autocomplete       │
 │ types     │   └──────┘   │ (rate limiting) │   │ Service            │
 │ "sup..."  │              └────────────────┘    └──────┬───────┬─────┘
 └──────────┘                                           │       │
                                                        ▼       ▼
                                              ┌──────────┐ ┌──────────────┐
                                              │  Trie    │ │ User History │
                                              │  Cache   │ │ Service      │
                                              │ (Redis)  │ │ (personal    │
                                              └────┬─────┘ │  results)    │
                                                   │       └──────┬───────┘
                                           cache miss             │
                                                   ▼              ▼
                                              ┌──────────┐   ┌─────────┐
                                              │  Trie    │   │ User DB │
                                              │ Storage  │   │(Postgres│
                                              │(persisted│   │ search  │
                                              │  trie)   │   │ history)│
                                              └──────────┘   └─────────┘


                                         DATA COLLECTION PATH (offline)
                                         ──────────────────────────────

 ┌──────────────┐   ┌──────────────────┐    ┌─────────────────┐    ┌──────────┐
 │ Completed    │──►│  Kafka           │──►│  Aggregation    │──►│  Trie    │
 │ search       │   │ (query logs)     │   │  Workers        │   │  Builder │
 │ queries      │   └──────────────────┘   │  (count freq    │   │ (rebuild │
 └──────────────┘                          │   per window)   │   │  + push  │
                                           └─────────────────┘   │  to cache│
                                                                 └──────────┘
```

### Data Flow

**Query path (user types "sup"):**
1. Client sends prefix "sup" to autocomplete service
2. Service checks **Trie cache** (Redis) → returns top K matches for "sup"
3. Optionally merges with **user's personal history** results
4. Returns ranked list: ["superhuman", "superbowl", "support", ...]

**Data collection path:**
1. Completed searches logged to **Kafka**
2. Aggregation workers count frequency per query per time window
3. Offline job rebuilds/updates the **Trie** periodically (every few minutes)
4. Updated Trie pushed to cache layer

---

## Deep Dive

### 1. Trie (The Core Data Structure)

**Why a Trie?**
- Prefix lookup is O(L) where L = length of prefix (fast)
- Natural fit for "starts with" queries
- Each node stores: character, children, top-K results for that prefix

```
Root
├── s
│   ├── u
│   │   ├── p  → top-K: ["superhuman", "superbowl", "support"]
│   │   │   ├── e
│   │   │   │   ├── r → top-K: ["superhuman", "superbowl", "superman"]
```

**Optimization:** Pre-compute and store top-K at each node. Avoids scanning all children at query time.

**Memory:** ~100M phrases × avg 20 chars × node overhead. Can be several GB. Fits in memory on beefy machines, or shard across nodes.

### 2. Ranking Suggestions

Rank by weighted score:
```
score = (frequency × recency_weight) + personalization_boost
```

| Factor | How |
|--------|-----|
| Frequency | Count of times query was searched globally |
| Recency | Recent queries weighted higher (time decay) |
| Personalization | Boost queries the specific user has searched before |
| Trending | Spike detection → boost suddenly popular queries |

### 3. Sharding the Trie

**Option A: Shard by prefix range**
- Server 1: a-f, Server 2: g-m, Server 3: n-s, Server 4: t-z
- Simple but uneven (some letters are much more common)

**Option B: Shard by hash of first N characters**
- More even distribution
- Client/router determines which shard to query

**Option C: Replicate entire trie**
- If it fits in memory (~few GB), just replicate to all nodes
- Simplest, fast reads, slightly delayed updates
- Works well up to moderate scale

### 4. Updating the Trie

**Don't update on every query** (too expensive). Instead:

1. Log all queries to Kafka
2. Every 5-15 minutes, aggregation job computes updated frequencies
3. Build new Trie version (or diff-update existing one)
4. Push to cache/serving nodes (blue-green swap)

**Trending queries:** Separate fast path - sliding window counter (last 1 hour) to detect spikes, inject into results.

### 5. Client-Side Optimizations

- **Debounce:** Don't send request on every keystroke. Wait 100-200ms after user stops typing.
- **Local cache:** Cache prefix→results on client. If user typed "sup" and got results, "supe" can filter client-side first.
- **Prefetch:** After "sup" returns, prefetch "supe", "suph", etc. in background.

### 6. Handling Offensive/Inappropriate Content

- Maintain a blocklist of terms
- Filter at Trie-build time (don't insert blocked terms)
- Manual review pipeline for flagged suggestions
- Important for professional / enterprise contexts: no offensive suggestions

---

## Key Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Trie vs Elasticsearch | Trie is faster for prefix search; ES is more flexible (fuzzy, typo-tolerant) but slower |
| Pre-computed top-K at nodes vs compute on query | Pre-computed = fast reads, stale data. On-query = fresh but slower |
| Update frequency (1 min vs 15 min) | More frequent = fresher suggestions, more compute cost |
| Full replication vs sharding | Replication = simpler, works if trie fits in memory. Sharding = needed at massive scale |
| Client debounce timing | Shorter = more responsive but more server load. Longer = fewer requests but feels laggy |

---

## Email / Productivity Product Angle

If framed around an email or productivity client:
- **Email search autocomplete** - suggest contacts, subjects, labels as user types
- **Command palette** - keyboard-first UX, suggest actions/shortcuts
- **"To:" field autocomplete** - rank by frequency of contact, recency of email
- Speed is typically brand-critical in these products - autocomplete MUST feel instant
