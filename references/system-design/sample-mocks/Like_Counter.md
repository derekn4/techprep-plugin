# System Design: Like Counter (Social Media)

**Source:** Practice walkthrough - February 23, 2026
**Variation of:** Distributed Counter, adapted for post likes with unlike support

---

## Problem

Design a system that counts likes on posts for a social media platform (like Instagram or Twitter). Users can like and unlike posts.

---

## Clarifying Questions & Answers

### Functional
- What are we counting? Post likes on a social media platform.
- Can counters decrement? Yes - users can unlike.
- Do we need historical data or just current total? Just current total. No time-series needed.

### Non-Functional
- Write-heavy. A viral post could get thousands of likes per second.
- Peak: ~10K likes/sec on a single popular post. Average across the system is much lower.
- ~100M unique counters (one per post).
- Approximate is acceptable for reads - being off briefly is fine. Eventually accurate.
- Read latency: under 100ms. Write latency: under 200ms.
- If a node goes down, no likes should be permanently lost.

---

## Back-of-Envelope Calculations

**Storage:**
- Like counts: 100M posts * 8 bytes = ~800MB (trivial)
- Like sets (who liked): 100M posts * avg 100 likes * 8 bytes per user ID = ~80GB
- Popular posts with millions of likes make individual sets larger

**Write throughput:**
- 1% of 100M posts are active at any time, averaging ~1 like/sec = ~1M writes/sec system-wide
- Single Redis instance handles ~100K-300K ops/sec, so dedup checks need sharded Redis (~4-10 nodes)

**Read throughput:**
- Write-heavy, assume 1:5 read-to-write ratio = ~200K reads/sec
- Simple key lookups, 1-2 Redis nodes handle this easily

**Kafka throughput:**
- 1M events/sec * ~100 bytes per event = ~100MB/sec
- Well within Kafka's capability

---

## Initial High-Level Design

Start simple:

```
Write: Client -> LB -> API Server -> NoSQL DB

Read:  Client -> LB -> API Server -> Redis (cache-aside + TTL) --miss--> DB
```

**DB choice:** NoSQL (Cassandra) - simple access pattern (insert, delete by composite key), 100M posts needs horizontal scaling, built-in sharding by post_id.

**Cache strategy:** Cache-aside with TTL. Since eventual consistency is fine, writes only go to the DB. On reads, check Redis first, cache miss falls through to DB, populate cache with TTL. Counts may be a few seconds stale, but that's acceptable per NFRs.

---

## Why a Dedup Set is Needed

The like set serves two purposes:

1. **Dedup / idempotency** - When a user likes a post, check "has this user already liked this post?" to prevent double-counting. Without it, a retry or duplicate request increments twice.
2. **Unlike support** - When a user unlikes, verify they actually liked first. Can't decrement if they never liked.

Without tracking who liked, the counter drifts from the true value over time.

---

## Evolved Design (Handling 10K likes/sec on a viral post)

### Problem 1: Hot partition
10K writes/sec on a single post_id = hot partition in the DB.

**Solution:** Add a message queue (Kafka) as a write buffer. Counter workers consume and batch writes. Instead of 10K individual writes, batch into a single `UPDATE` every few hundred milliseconds. DB sees fewer, larger writes.

### Problem 2: 1M total writes/sec
DB can't keep up with 1M direct writes/sec.

**Solution:** Same answer - Kafka decouples write ingestion speed from DB write speed.

### Problem 3: Dedup consistency
On every like: read the user set AND write to it AND track the count = multiple operations.

**Solution:** Move dedup to Redis. `SISMEMBER` checks if user already liked. `SADD` returns 0 if member already exists, so the check and insert is a single atomic operation.

### Evolved Design

```
                        WRITE PATH
                        ----------
  Client --POST like--> LB --> API Server
                                  |
                                  v
                          ┌──────────────┐
                          │ Redis SET    │ SISMEMBER: already liked?
                          │ (dedup)      │ SADD: record the like
                          └──────┬───────┘
                                 │ new like? publish event
                                 v
                          ┌──────────────┐
                          │    Kafka     │ partitioned by post_id
                          │              │ buffers spikes, retains for replay
                          └──────┬───────┘
                                 │ consume + batch in memory
                                 v
                          ┌──────────────┐
                          │   Counter    │ batch 10K events into
                          │   Workers    │ one write every 500ms
                          └──────┬───────┘
                                 │ idempotent write (batch_id)
                                 v
                          ┌──────────────┐
                          │  Cassandra   │ source of truth
                          │  (batches +  │ counter_batches: SUM(delta)
                          │   post_likes)│ post_likes: who liked
                          └──────────────┘


                        READ PATH
                        ---------
  Client --GET count--> LB --> API Server
                                  |
                                  v
                          ┌──────────────┐
                          │ Redis STRING │ GET post:{id}:count
                          │ (count cache)│
                          └──────┬───────┘
                                 │
                          hit?   │   miss?
                        ┌────────┴────────┐
                        v                 v
                  return count     ┌──────────────┐
                  to client        │  Cassandra   │ SUM(delta) for post
                                   └──────┬───────┘
                                          │
                                          v
                                   populate Redis cache (TTL)
                                          │
                                          v
                                   return count to client
```

**Write path:**
1. API server checks Redis: `SISMEMBER post:{id}:likes user_456`
2. If already liked - reject or silently ignore
3. If new like - `SADD post:{id}:likes user_456`, publish event to Kafka
4. Counter workers consume from Kafka, batch events in memory
5. Every 500ms, flush batch to Cassandra with idempotent write

**Read path:**
1. Check Redis: `GET post:{id}:count`
2. Cache hit - return count
3. Cache miss - query Cassandra, populate Redis with TTL, return count

Workers do NOT update Redis count. TTL expiry triggers recalculation on next read miss. Eventual consistency is fine per NFRs.

---

## Redis Contents

Two separate concerns, same cluster with different key patterns:

| Key Pattern | Type | Purpose | Used By |
|---|---|---|---|
| `post:{id}:likes` | SET | User IDs who liked (dedup) | API server, write path |
| `post:{id}:count` | STRING | Cached like count | API server, read path |

Both keyed by post_id so they shard similarly. Could split into separate clusters if needed (dedup is write-heavy, count cache is read-heavy).

---

## Cassandra Idempotency Fix

**Problem:** Cassandra counter columns are not idempotent. If a worker flushes `INCREMENT BY 50`, the write times out but actually went through, and the worker retries, you get +100 instead of +50.

**Solution:** Store batches with a unique batch_id instead of using counter columns:

```
counter_batches (
    post_id     BIGINT    -- partition key
    batch_id    UUID      -- clustering key
    delta       INT       -- +295, -3, etc.
)
```

Each flush writes a row with a unique batch_id. Retry = same batch_id = Cassandra upserts, no double counting. Count is derived by `SUM(delta)`, cached in Redis so you're not querying Cassandra on every read.

Also store individual likes for rebuilding Redis dedup sets on recovery:

```
post_likes (
    post_id     BIGINT    -- partition key
    user_id     BIGINT    -- clustering key
)
```

**Compaction:** Background job periodically reads all batch rows for a post, sums into a single row, deletes old ones. Keeps the table small per post.

---

## Failure Handling

| Scenario | What Happens |
|---|---|
| **Redis down between dedup and Kafka** | Like is in Redis set but never reaches Kafka/DB. On Redis recovery (rebuild from DB), set is missing this like, user can like again - self-corrects. |
| **Kafka gets event but worker crashes** | Kafka retains event (offset not committed). Worker reprocesses on restart. batch_id makes the write idempotent. |
| **Worker crashes before flush** | In-memory batch lost, but events still in Kafka. Offset not committed, events replayed. At most 500ms of aggregation work lost, not actual events. |
| **Cassandra down** | Kafka buffers events until recovery. |
| **Redis dedup set lost** | Rebuild from Cassandra post_likes table. |

---

## Key Differences from Generic Distributed Counter

| | Generic Counter | Like Counter |
|---|---|---|
| **Decrement** | No | Yes (unlikes) |
| **Dedup needed** | No (just count events) | Yes (one like per user) |
| **In-memory buffering** | On API servers before Kafka | No - API server publishes directly to Kafka |
| **Time-series** | Yes (time-bucketed rollups) | No (just current total) |
| **Redis on write path** | Workers update Redis | No - cache-aside with TTL only |

Same core pipeline (API -> Kafka -> Workers -> Cassandra + Redis), different requirements drive different details.

---

## Key Tradeoffs Discussed

| Decision | Tradeoff |
|---|---|
| Cache-aside + TTL vs write-through | TTL is simpler, accepts staleness. Write-through is overkill for eventual consistency. |
| Redis dedup vs Postgres PK constraint | Redis is faster for hot path. Postgres PK works for initial simple design. |
| Kafka buffering vs direct DB write | Kafka adds a component but absorbs spikes and provides replay on failure. |
| Cassandra batch_id vs counter columns | batch_id adds read complexity (SUM) but guarantees idempotency on retries. |
| 500ms flush interval | Shorter = more DB writes. Longer = more data at risk in memory. 500ms balances both. |

---

## Core Takeaways to Remember

**Components and why each exists:**
- **Redis Set** - dedup on the hot write path. SISMEMBER + SADD is atomic. Without it, retries and duplicates corrupt the count.
- **Kafka** - decouples write ingestion from DB write speed. Buffers spikes, retains events for replay on failure.
- **Counter Workers** - batch many small writes into fewer large writes. Turns 10K/sec into one write every 500ms.
- **Cassandra** - horizontally scalable write-heavy store. Source of truth.
- **Redis Cache** - serves read count with cache-aside + TTL. Keeps Cassandra off the hot read path.

**Key intuitions:**
1. **Start simple, scale when pushed.** Initial design is just API -> DB + cache. Add Kafka and workers only when the interviewer asks about hot partitions or write throughput.
2. **Unlike support = you must track WHO liked.** A simple counter isn't enough. You need a set per post for dedup and unlike validation.
3. **Don't update Redis count on writes if eventual consistency is fine.** Let the TTL handle it. Simpler write path, less coupling.
4. **Cassandra counters aren't idempotent.** Use batch_id rows + SUM(delta) instead. Retries are safe because same batch_id upserts.
5. **Worker crash doesn't lose events.** Kafka retains them. Only the in-memory aggregation batch is lost, and it replays automatically.
6. **The read aggregation (SUM) is expensive but rare.** Redis caches it. Only computed on cache miss. Periodic compaction keeps the table small.
7. **10K/sec is the peak for ONE post, not the system.** Most posts are dormant. Estimate system-wide by asking what % of posts are active.
