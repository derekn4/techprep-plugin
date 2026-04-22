# System Design: Distributed Counter

**Source:** Common system design interview question (variation of this)

---

## Overview

Design a system that accurately counts events (page views, likes, API calls, etc.) across multiple servers at high scale. The core challenge: **how do you maintain an accurate count when thousands of servers are incrementing simultaneously?**

---

## Clarifying Questions & Answers

| Question | Answer |
|----------|--------|
| What are we counting? (page views, likes, clicks?) | Could be any - assume generic event counter (e.g., page views per URL) |
| What's the expected write throughput? | Millions of increments per second across all counters |
| How many unique counters? | Millions (e.g., one per page/URL) |
| Do we need exact counts or approximate? | Near-real-time approximate is fine; eventual exact count |
| What read latency is acceptable? | Reads can tolerate slight staleness (~seconds) |
| Do counters ever decrement? | No, increment only (simplifies the problem) |
| Do we need historical data (counts over time) or just current total? | Both - current total + ability to query time ranges |
| Is there a geographic distribution requirement? | Yes, multi-region |
| What happens if a node goes down mid-count? | Small loss acceptable, but minimize it |

---

## Requirements

### Functional
- **Increment** a counter by key (e.g., `increment("page:/home")`)
- **Read** current count for a given key
- **Query** counts over a time range (last hour, last day)
- Support millions of distinct counters

### Non-Functional
- **High throughput:** Handle millions of writes/sec
- **Low write latency:** Increment should return fast (<10ms)
- **Scalability:** Horizontally scalable as traffic grows
- **Durability:** Don't lose counts permanently
- **Availability:** Prioritize availability over strong consistency (AP in CAP)
- **Eventual consistency:** Reads can be slightly stale (seconds, not minutes)

---

## High-Level Design

```
                        ┌─────────────────────────────────────────────┐
                        │         API Servers (stateless)              │
                        │  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
 ┌────────┐  ┌──────┐  │  │ In-Memory │ │ In-Memory │ │ In-Memory │ │
 │Clients │─►│  LB  │─►│  │  Counter  │ │  Counter  │ │  Counter  │ │
 │web/mob/│  └──────┘  │  │  HashMap  │ │  HashMap  │ │  HashMap  │ │
 │services│             │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ │
 └────────┘             └───────┼──────────────┼──────────────┼───────┘
                                │   flush every 1-5 sec       │
                                ▼              ▼              ▼
                        ┌─────────────────────────────────────────────┐
                        │           Kafka (partitioned by key)        │
                        └──────────────────────┬──────────────────────┘
                                               │
                                               ▼
                        ┌─────────────────────────────────────────────┐
                        │       Aggregation Workers (batch-sum)       │
                        └────────────┬────────────────────┬───────────┘
                                     │                    │
                                     ▼                    ▼
                          ┌──────────────────┐  ┌─────────────────┐
                          │   Cassandra      │  │  Redis Cache    │
                          │  (durable store, │  │ (fast reads,    │
                          │   time-bucketed) │  │  slightly stale)│
                          └──────────────────┘  └─────────────────┘
                                     ▲                    │
                                     │   cache miss       │
                                     └────────────────────┘

Read path:  Client -> LB -> API Server -> Redis Cache -> (miss) -> Cassandra
```

### Data Flow

**Write path (increment):**
1. Client calls `POST /counters/{key}/increment`
2. API server increments an **in-memory local counter** (per key, per node)
3. Every N seconds (or N increments), flush batch to **Kafka**
4. Aggregation workers consume from Kafka, batch-sum, write to DB
5. Update Redis cache with new total

**Read path (get count):**
1. Client calls `GET /counters/{key}`
2. Read from **Redis cache** (fast, slightly stale)
3. Cache miss → read from DB, populate cache

---

## Deep Dive

### 1. In-Memory Local Aggregation (The Key Insight)

**Problem:** If every increment hits the database, you'll kill it at scale.

**Solution:** Each API server keeps a local `HashMap<key, count>` in memory.
- Increment is just `map[key] += 1` (nanoseconds, no network)
- Flush to Kafka every 1-5 seconds as a batch: `{key: "page:/home", count: 347, timestamp: ...}`
- This turns millions of individual writes into thousands of batched writes

**Tradeoff:** If a node crashes before flushing, you lose that window of counts (1-5 sec worth). Acceptable for most use cases.

### 2. Why Kafka (Message Queue)?

- **Decouples** write speed from DB write speed
- **Durability** - messages persist even if workers are down
- **Replay** - can reprocess if aggregation worker had a bug
- Partition by counter key for ordered processing per key
- Handles burst traffic without overwhelming downstream

### 3. Database Choice

**Option A: Cassandra (wide-column store)** - Best for this use case
- Write-optimized, handles high throughput natively
- Natural time-series support with clustering keys
- Schema: `(counter_key, time_bucket) -> count`
- Horizontally scalable, no single point of failure

**Option B: PostgreSQL with partitioning**
- Simpler, works at moderate scale
- Use time-based partitions for historical queries
- Needs sharding at very high scale

**Option C: Redis (as primary store)**
- `INCRBY` is atomic and fast
- Risk: data loss if Redis crashes (even with AOF)
- Better as cache layer, not sole source of truth

**Recommendation:** Cassandra for durability + Redis for fast reads.

### 4. Handling Hot Keys (e.g., viral post)

**Problem:** One counter getting 100x normal traffic (a viral page).

**Solutions:**
- **Shard the counter:** Split `page:/viral` into `page:/viral:shard0`, `page:/viral:shard1`, ... `page:/viral:shardN`. Read = sum all shards.
- **Random shard assignment:** Each API node writes to a random shard. Spreads write load.
- **More aggressive local buffering:** Increase flush interval for hot keys specifically.

### 5. Exact vs. Approximate Counting

| Approach | Accuracy | Memory | Speed |
|----------|----------|--------|-------|
| Exact (sum all batches) | 100% | High | Slower reads |
| HyperLogLog | ~98% (for unique counts) | Very low | Fast |
| Count-Min Sketch | Approximate | Low | Fast |

For simple increment counters, exact is straightforward with batching. HyperLogLog is for **unique** counting (distinct users), not total events.

### 6. Time-Range Queries

Store counts in **time buckets** for efficient range queries:

```
Table: counter_rollups
| counter_key  | time_bucket (1-min) | count |
|-------------|---------------------|-------|
| page:/home  | 2026-02-09 14:00    | 12847 |
| page:/home  | 2026-02-09 14:01    | 13102 |
```

- Workers aggregate into 1-minute buckets
- Background job rolls up: 1-min → 1-hour → 1-day buckets
- Query "last hour" = sum 60 one-minute buckets
- Query "last 30 days" = sum 30 one-day buckets

### 7. Multi-Region

- Each region has its own local counter pipeline
- Async replication of aggregated counts between regions
- Read from local region (fast), accept slight cross-region staleness
- Global total = sum of all regional totals (computed periodically)

---

## Key Tradeoffs to Discuss

| Decision | Tradeoff |
|----------|----------|
| Local buffering window (1s vs 5s) | Shorter = more accurate, more DB load. Longer = less load, more data loss risk |
| Kafka vs direct DB write | Kafka adds latency but absorbs spikes and adds durability |
| Cassandra vs Postgres | Cassandra scales writes better but more operational complexity |
| Exact vs approximate | Exact needs more storage/compute but gives real numbers |
| Sharding hot keys | Adds read complexity (sum shards) but handles viral content |

---

## Email Product Angle

If they frame it as email-related, think:
- **Email open tracking** - count how many times an email was opened
- **Link click counting** - track clicks on links in emails
- **Unread count** - per-user unread email counter (this is a decrement case too)
- **Analytics dashboard** - emails sent/received per user over time

Same architecture applies, just different counter keys.
