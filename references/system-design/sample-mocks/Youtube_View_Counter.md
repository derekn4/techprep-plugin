# System Design Mock #7: YouTube View Counter

**Date:** February 26, 2026
**Rating:** Practice Mock (self-study)

---

## Problem

Design YouTube's video view counter. When a user watches a video, the view count increments. The count is displayed on every video page. You need to handle viral videos that get millions of views per minute.

## Requirements Gathered

### Functional
- Increment view count when a user watches a video
- Read current view count for a given video
- View count displayed on video page (does not need to be exact in real-time)
- Analytics: query view counts over time ranges (last hour, last day, last 30 days)
- Basic deduplication: same user watching the same video repeatedly in a short window shouldn't count as multiple views

### Non-Functional
- Scale: 1B daily active users, ~5B video views/day (~58K views/sec avg, ~200K/sec peak)
- Write latency: increment should return fast (<10ms to client)
- Read latency: view count reads should be fast (<50ms)
- Eventual consistency: count can be stale by a few seconds
- Durability: don't permanently lose counts (small window of loss on crash is acceptable)
- Availability over consistency (AP)

---

## Back-of-Envelope

- 5B views/day / 86,400 sec = ~58K/sec average
- Peak: 3-4x average = ~200K/sec (viral video + prime time)
- Viral video spike: single video could get 50K views/sec
- Storage: 1B videos x 8 bytes (counter) = ~8GB for current totals (tiny)
- Time-bucketed analytics: 1B videos x 365 days x 8 bytes = ~2.9TB/year (manageable with Cassandra)

---

## High-Level Design

```
                           INGESTION
                           ---------
  Client (video player)
        |
        v
  ┌──────────┐     ┌──────────────────┐
  │    LB    │────>│   API Servers    │
  └──────────┘     │  (stateless)     │
                   │  ┌────────────┐  │
                   │  │ In-Memory  │  │
                   │  │ Counter    │  │
                   │  │ HashMap    │  │
                   │  └─────┬──────┘  │
                   └────────┼─────────┘
                            │ flush every 1-5 sec
                   BUFFERING│
                   ---------│
                            v
                   ┌─────────────────┐
                   │ Kafka           │
                   │ (partitioned    │
                   │  by video_id)   │
                   └────────┬────────┘
                            │
                   AGGREGATION
                   -----------
                            v
                   ┌─────────────────┐
                   │ Aggregation     │
                   │ Workers         │
                   │ (batch-sum per  │
                   │  time bucket)   │
                   └───────┬─────────┘
                           │
                   STORAGE │
                   --------│
                   ┌───────┴─────────┐
                   v                 v
          ┌──────────────┐   ┌──────────────┐
          │  Cassandra   │   │    Redis     │
          │ (time-bucket │   │ (current     │
          │  rollups,    │   │  totals,     │
          │  durable)    │   │  fast reads) │
          └──────────────┘   └──────────────┘

Write path: Client -> LB -> API Server (in-memory INCR) -> flush -> Kafka -> Workers -> Cassandra + Redis
Read path:  Client -> LB -> API Server -> Redis (hit? return) -> miss -> Cassandra (sum buckets)
```

---

## Key Design Decisions

### 1. In-Memory Aggregation on API Servers

**Why not write directly to Redis or DB per request?**
- At 200K/sec peak, even Redis would struggle as a single write target
- Each API server buffers increments locally: `map[video_id] += 1`
- Flush to Kafka every 1-5 seconds as a batch: `{video_id: "abc123", count: 1,847, window: "14:05:01-14:05:05"}`
- Turns 200K individual writes/sec into a few thousand batched writes/sec

**Tradeoff:** Server crash before flush loses 1-5 seconds of counts. For view counts, nobody notices if a video shows 14,238,471 instead of 14,238,519.

### 2. Kafka as Buffer

- Decouples ingestion speed from storage speed
- Partitioned by `video_id` so all counts for one video go to the same partition (ordered processing)
- Durable: once flushed to Kafka, counts survive even if aggregation workers go down
- Replay: if a worker bug miscounted, replay from Kafka offset to recompute

### 3. Aggregation Workers (Batch-Sum)

Workers consume from Kafka and do two things:
1. **Update current total in Redis:** `INCRBY video:abc123 1847`
2. **Write time-bucketed row to Cassandra:** `(video_id, 1-min bucket) -> count`

Workers are stateless and horizontally scalable. More partitions = more workers.

### 4. Storage: Cassandra (Analytics) + Redis (Current Total)

**Cassandra** for durable, time-bucketed storage:
- Schema: `partition_key: video_id, clustering_key: time_bucket, value: count`
- Supports time-range queries: "views in the last hour" = sum 60 one-minute buckets
- Write-optimized, handles the throughput
- Background rollup jobs: 1-min -> 1-hour -> 1-day buckets

**Redis** for fast current-total reads:
- Single key per video: `video:abc123 -> 14238471`
- Updated by aggregation workers via `INCRBY`
- Every video page load reads from here (sub-ms)
- If Redis goes down, fall back to Cassandra (sum all buckets for that video, slower)

### 5. Handling Viral Videos (Hot Key Problem)

A viral video might get 50K views/sec, all mapping to the same Kafka partition.

**Solutions:**
- **In-memory aggregation already helps:** 50K/sec across 100 API servers = 500 views/server/sec, each server flushes one batch per second. Kafka partition receives ~100 messages/sec, not 50K.
- **If still hot:** shard the Kafka partition key: `video_id:shard0`, `video_id:shard1`, etc. Multiple workers process in parallel. Redis key stays unshareded since `INCRBY` from multiple workers is fine (atomic).
- **If Redis key becomes hot:** use Redis read replicas for the read side. Writes still go to primary.

### 6. Basic View Deduplication

**Goal:** Same user re-watching or refreshing shouldn't inflate counts unreasonably.

**Approach:**
- On the API server, check a **Bloom filter** (per video, short-lived) or a Redis set with TTL
- Key: `dedup:{video_id}:{user_id}`, TTL: 30 seconds
- If key exists, skip the increment
- Not perfect (Bloom filter has false positives, TTL window is short), but good enough
- YouTube doesn't need exact dedup, just reasonable filtering

**Why not exact dedup?**
- Storing every (user_id, video_id) pair permanently is expensive at scale
- Exact dedup requires a distributed set lookup on every view, adds latency
- Approximate is the pragmatic choice for view counts

---

## Deep Dives

### Scaling to 2M/sec (10x)

1. **More API servers** - in-memory aggregation scales linearly
2. **More Kafka partitions** - spread across more brokers
3. **More aggregation workers** - one per partition
4. **Shard Redis** - if single Redis can't handle the INCRBY throughput (unlikely since batching reduces it significantly)
5. **Cassandra scales naturally** - add more nodes, data distributes automatically

### What Happens When Redis Goes Down?

- **Reads fall back to Cassandra:** sum time buckets for the requested video. Slower (100ms vs 1ms) but functional.
- **Writes buffer in Kafka:** aggregation workers retry writing to Redis. Kafka retains messages.
- **Recovery:** when Redis comes back, workers catch up from Kafka. Or rebuild from Cassandra totals.

### Time-Range Analytics

```
Table: view_rollups
| video_id | time_bucket (1-min) | count  |
|----------|---------------------|--------|
| abc123   | 2026-02-26 14:00    | 12,847 |
| abc123   | 2026-02-26 14:01    | 13,102 |

Background rollup jobs:
  1-min buckets -> 1-hour buckets -> 1-day buckets

Query "views in last hour":  sum 60 one-minute buckets
Query "views in last 30 days": sum 30 one-day buckets
```

### Monitoring

| Metric | What It Tells You |
|--------|-------------------|
| Flush lag per API server | Are servers buffering too long? Could indicate backpressure |
| Kafka consumer lag | Are aggregation workers keeping up? |
| Redis vs Cassandra count drift | Are counts consistent? Large drift = bug in pipeline |
| View count rate per video | Detect bot traffic or abuse (sudden unnatural spikes) |
| Dedup hit rate | What percentage of views are being filtered? Too high = possible bot |

---

## Evaluation

### Why This Design Works

- **In-memory aggregation** is the critical insight. It's what makes 200K/sec feasible without melting the database.
- **Kafka partitioned by video_id** ensures ordered processing per video and provides durability after the volatile in-memory stage.
- **Two storage systems** serve different access patterns: Redis for "show me the number now" (every page load), Cassandra for "show me the trend over time" (analytics dashboard).
- **Eventual consistency** is perfectly acceptable. Nobody cares if a view count is 3 seconds stale.

### Areas an Interviewer Might Push On

1. **"What about exactly-once counting?"** - Not worth the cost. At-least-once with approximate dedup is the industry standard for view counts.
2. **"How do you know a view is real?"** - Separate fraud detection system (ML-based), out of scope for the counter design. Mention it exists but don't design it.
3. **"What if Kafka goes down?"** - API servers continue buffering in memory (extend flush window). If they fill up, start dropping or writing directly to Redis as fallback. Kafka downtime should be rare and brief.
4. **"Why not just use sharded Redis without Kafka?"** - Could work at moderate scale. But at 200K/sec, in-memory aggregation reduces write volume by 100-1000x before it even hits the network. Sharded Redis still sends every increment over the network.

---

## Connection to Counter Variations

This is the **full-scale version** of the Kafka + in-memory aggregation pattern from `Distributed_Counter.md`. The Counter Variations file shows how the same problem changes when NFRs change:

| If the interviewer says... | You pivot to... |
|---|---|
| "View counts, massive scale" | This design (in-memory agg + Kafka + Cassandra) |
| "But what if counts must be exact?" | Variation 1: Direct DB write (Postgres ACID) |
| "Simpler, moderate scale?" | Variation 2: Single Redis INCR |
| "More throughput than single Redis, but no Kafka?" | Variation 3: Sharded Redis |

The view counter is the poster child for why in-memory aggregation exists: extremely high write throughput where losing a few seconds of counts on crash is a non-issue.
