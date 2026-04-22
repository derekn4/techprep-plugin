# Step 3: Capacity Estimation (Back-of-Envelope)

> **Goal:** Estimate scale and connect it to architecture decisions. ~3 minutes. State assumptions, don't ask questions.

---

## The 4 Dimensions

Everything derives from **traffic**. Estimate traffic first, then multiply through:

```
Traffic (QPS)
  |-- x payload size     = Bandwidth
  |-- x record size x retention = Storage
  |-- x cache ratio      = Memory
```

| Dimension | What you're estimating | Formula | Units |
|---|---|---|---|
| **Traffic** | How many requests/sec? | DAU x actions/user/day / 86,400 | QPS |
| **Storage** | How much disk over time? | QPS x record size x seconds in retention period | GB/TB |
| **Bandwidth** | How much network I/O? | QPS x avg payload size | MB/s |
| **Memory** | How much RAM for caching? | Cache the hot subset (80/20 rule or explicit %) | GB |

---

## Target: 0 Clarifying Questions, 2-3 Minutes, State Assumptions

You're not asking the interviewer anything here. You state assumptions and let them correct you. Focus on Traffic and Storage -- those two drive architecture decisions. Only do Bandwidth and Memory if they're clearly relevant (large payloads, or you need to justify cache sizing).

---

## Step-by-Step Flow

**Step 1: Traffic (always start here)**
```
Given: 10M DAU, each user sends 20 messages/day

Write QPS = 10M x 20 / 86,400 ~ 2,300 QPS
Peak QPS  = 2,300 x 2 (or x3) ~ 5,000 QPS (assume 2-3x peak factor)

Read:Write ratio? Chat is ~10:1 reads per write
Read QPS  = 2,300 x 10 ~ 23,000 QPS
```
**Shortcut:** 86,400 seconds/day ~ ~100K. So "X per day" / 100K ~ QPS. (Slightly overestimates, which is fine for estimation.)

**Step 2: Storage**
```
Per message: sender_id (8B) + receiver_id (8B) + text (500B avg) + metadata (100B) ~ 600B

Daily:  2,300 QPS x 86,400 sec x 600B ~ 120 GB/day
Yearly: 120 GB x 365 ~ 43 TB/year

With replication (x3): ~130 TB/year
```

**Step 3: Bandwidth**
```
Incoming (writes): 2,300 QPS x 600B ~ 1.4 MB/s
Outgoing (reads):  23,000 QPS x 600B ~ 14 MB/s

Not a bottleneck here. Bandwidth matters more when payloads are large (images, videos).
```

**Step 4: Memory (Cache)**
```
80/20 rule: 20% of data serves 80% of reads

Daily data: 120 GB
Cache 20%:  120 GB x 0.20 = 24 GB  (fits in a single Redis instance)

Or: cache the last N hours of messages
Last 1 hour: 2,300 x 3,600 x 600B ~ 5 GB
```

---

## Numbers You Should Know

**Latency (order of magnitude):**

| Operation | Latency |
|---|---|
| L1 cache | ~1 ns |
| RAM access | ~100 ns |
| SSD read | ~100 us |
| Network round-trip (same DC) | ~500 us |
| HDD seek | ~10 ms |
| Network round-trip (cross-continent) | ~150 ms |

**Scale shortcuts:**

| Shortcut | Value |
|---|---|
| Seconds in a day | ~86,400 ~ ~100K |
| Seconds in a month | ~2.5M |
| Seconds in a year | ~31.5M ~ ~30M |
| 1 million bytes | ~1 MB |
| 1 billion bytes | ~1 GB |
| 1 trillion bytes | ~1 TB |

**Capacity rules of thumb:**

| Resource | Rough capacity |
|---|---|
| Single Redis instance | ~25-100 GB RAM, ~100K QPS |
| Single Postgres | ~1-5 TB, ~10K QPS (depends on query complexity) |
| Single Kafka broker | ~50-100K messages/sec |
| Single web server | ~1-10K QPS (depends on work per request) |

---

## When Each Dimension Actually Matters

Not every problem needs all 4. Focus on the ones that drive architecture decisions:

| Dimension | When it drives decisions | Example |
|---|---|---|
| **Traffic** | Always - determines how many servers, whether you need sharding | "50K QPS means we need multiple DB shards" |
| **Storage** | When data grows unbounded or retention is long | "43 TB/year means we need partitioning strategy" |
| **Bandwidth** | When payloads are large (media, files) | "Users upload 5MB images at 1K QPS = 5 GB/s incoming" |
| **Memory** | When you need to justify cache sizing or in-memory stores | "24 GB hot set fits in one Redis box" |

---

## Interview Tips

- **Round aggressively.** 86,400 ~ 100K. Nobody expects precision.
- **State assumptions out loud.** "I'll assume 10M DAU with 20 messages per user per day" - let the interviewer correct you.
- **Connect estimates to decisions.** Don't just calculate - say what it means: "23K read QPS means we need caching" or "43 TB/year means we need a partitioning strategy."
- **Peak vs average.** Multiply average by 2-3x for peak. If you're designing for peak, say so.
- **Don't spend more than 3-5 minutes.** This is a means to an end (justifying architecture choices), not the goal itself.

---

## Quick Template (Copy This)

```
Assumptions:
- DAU: ___
- Actions per user per day: ___
- Avg payload/record size: ___

Traffic:
- Write QPS: ___ DAU x ___ actions / 100K ~ ___ QPS
- Read:Write ratio: ___:1
- Read QPS: ___ x ___ ~ ___ QPS
- Peak: x2-3 -> ___ QPS

Storage:
- Per record: ___ bytes
- Daily: ___ QPS x 86,400 x ___ bytes ~ ___ GB/day
- Yearly: ___ x 365 ~ ___ TB/year
- With replication (x3): ___

Bandwidth:
- In:  ___ write QPS x ___ bytes ~ ___ MB/s
- Out: ___ read QPS x ___ bytes ~ ___ MB/s

Memory (Cache):
- 80/20 rule: daily ___ GB x 0.2 ~ ___ GB
- Or cache last ___ hours: ___

-> Architecture implication: ___
```
