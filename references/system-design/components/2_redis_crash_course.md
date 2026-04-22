# Redis Crash Course for System Design

---

## Quick Reference (Read This First)

Redis is an in-memory key-value data store. That's it at its core. Everything else is just features built on top of that.

For interviews, know these 3 use cases:

1. **Cache** - the most common. Store hot data in memory for fast reads. URL shortener, product pages, user profiles. This is 90% of how you'll use it in interviews.
2. **Counter / rate limiter** - INCR is atomic, so it's perfect for counters (like your URL shortener key generation), rate limiting (track requests per user per minute), and view counts.
3. **Session store** - fast auth checks on every request, TTL for expiration.

That's it for the core interview use cases. If you say "Redis" in an interview, you mean one of those three things.

### Things You Do NOT Need to Know

- **Pub/sub** - relevant for message queue designs, but you'd use Kafka instead 99% of the time
- **Streams** - niche, skip it
- **Sentinel** - just know "Redis has built-in failover support" if asked
- **Cluster** - just know "Redis can shard across multiple nodes for horizontal scaling"
- **Data structures (sorted sets, hyperloglogs, etc.)** - skip unless specifically asked

### Interview Cheat Sheet

| Need... | Say... |
|---|---|
| Fast reads? | "Redis as a cache" |
| Atomic counter? | "Redis INCR" |
| Session storage? | "Redis as primary store with TTL" |
| Asked about Redis availability? | "Leader-follower replication with promotion" |

That covers most scenarios you'll encounter.

---

## Detailed Reference (Below)

## What It Is
In-memory key-value data store. Think of it as a giant hash map that lives in RAM. Often used as a cache, session store, message broker, and real-time leaderboard engine.

## Performance
- **Read/Write latency:** ~1ms or sub-millisecond (single-digit microseconds for simple ops)
- **Throughput:** ~100K-300K+ ops/sec on a single node
- **Why so fast:** Everything in memory, single-threaded event loop (no lock contention), efficient C implementation, I/O multiplexing

## Core Data Structures
- **Strings** - basic get/set, counters (INCR)
- **Hashes** - field-value pairs under one key (great for objects)
- **Lists** - linked lists, good for queues (LPUSH/RPOP)
- **Sets** - unique members, intersections/unions
- **Sorted Sets (ZSETs)** - ranked members by score -> leaderboards, rate limiters, priority queues

**Bonus structures** (know they exist, don't need to memorize details):
- **Streams** - durable append-only log, like a lightweight Kafka
- **HyperLogLog** - probabilistic unique counting (e.g., unique visitors)
- **Bitmaps** - bit-level ops (e.g., daily active user tracking)

## Persistence
Two options: **RDB** (periodic snapshots - fast recovery, gaps between snapshots) and **AOF** (logs every write - more durable, slower recovery). Can use both together. Know the tradeoff: durability vs. recovery speed.

## Replication & High Availability
- **Master-replica** replication (async by default) for read scaling and failover
- Async replication means a small window for data loss on failover
- **Redis Sentinel** - monitors master/replicas and performs automatic failover (promotes a replica to master). Provides HA but does NOT provide sharding.
- **Redis Cluster** - horizontal scaling via automatic sharding across nodes, with built-in failover (no Sentinel needed). Use when you outgrow a single node.

## Atomicity
- **MULTI/EXEC** - batch commands atomically (all-or-nothing execution, no rollback)
- **Lua scripting** - complex atomic operations server-side

## Pub/Sub
- Fire-and-forget messaging. No persistence, no acknowledgment. If subscriber is down, messages are lost.
- Use **Streams** instead if you need durability or consumer groups

## Common System Design Use Cases

| Use Case | How |
|---|---|
| **Cache** | TTL-based caching, cache-aside/write-through |
| **Session store** | Fast user session lookups |
| **Rate limiter** | INCR + EXPIRE or sliding window with sorted sets |
| **Leaderboard** | Sorted sets (ZADD, ZRANK, ZRANGE) |
| **Dedup / membership** | Sets (SADD returns 0 if duplicate, SISMEMBER to check) |
| **Distributed lock** | SET NX EX (or Redlock for multi-node) |
| **Message queue** | Lists (LPUSH/BRPOP) or Streams |
| **Real-time analytics** | HyperLogLog, bitmaps, sorted sets |

## Redis Commands in Action (What You'd Actually Say in an Interview)

**Rate Limiter (fixed window):**
```
INCR  user123:1740307200    -> 1  (key auto-created, first request this window)
INCR  user123:1740307200    -> 2  (same window, count goes up)
EXPIRE user123:1740307200 60     (auto-delete after 60s so stale keys don't pile up)
# If INCR returns > limit -> reject with 429
```
Key pattern: `client_id:window_timestamp`. Each window gets a fresh key. INCR is atomic so no race conditions even under high concurrency.

**Distributed Lock:**
```
SET lock:order_123 owner_id NX EX 30
# NX = only set if key doesn't exist (acquire lock)
# EX 30 = auto-expire in 30s (prevents deadlock if holder crashes)
# Returns OK -> lock acquired. Returns nil -> someone else holds it.
DEL lock:order_123              (release lock when done)
```

**Leaderboard:**
```
ZADD leaderboard 1500 "alice"   (add/update alice with score 1500)
ZADD leaderboard 2300 "bob"     (add/update bob with score 2300)
ZREVRANGE leaderboard 0 9       (top 10 players, highest score first)
ZRANK leaderboard "alice"       (alice's rank, 0-indexed)
ZINCRBY leaderboard 100 "alice" (atomically add 100 to alice's score)
```

**Dedup / Membership Check (Sets):**
```
SADD  post:789:likes user_456    -> 1  (added, user hadn't liked before)
SADD  post:789:likes user_456    -> 0  (already exists, duplicate - skip)
SISMEMBER post:789:likes user_456 -> 1  (check without adding)
SREM  post:789:likes user_456    -> 1  (removed, for unlike)
SCARD post:789:likes             -> 42 (total unique members in set)
```
SADD doubles as check + insert in one atomic op. Return value tells you if it was new (1) or duplicate (0). Use for like dedup, tracking unique visitors, or any "has this been seen before?" check.

**Cache (cache-aside pattern):**
```
GET cache:user:456              (check cache first)
# If nil -> query DB, then:
SET cache:user:456 "{json}" EX 3600  (cache result with 1hr TTL)
```

**Session Store:**
```
SET session:abc123 "{user_id: 456, role: admin}" EX 1800  (30min session)
GET session:abc123              (look up session on each request)
```

**Message Queue:**
```
LPUSH queue:emails "{to: user@x.com, body: ...}"  (producer pushes)
BRPOP queue:emails 30           (consumer blocks up to 30s waiting for work)
```

## Key Limitations to Mention in Interviews
- **Memory-bound** - expensive at scale compared to disk-based stores
- **Single-threaded** for command execution (I/O is multithreaded in Redis 6+) - one slow command blocks everything
- **Async replication** - potential data loss on failover
- **Not a replacement for a database** - use it alongside one

## Quick Numbers to Remember

| Metric | Value |
|---|---|
| Latency | < 1ms |
| Throughput | ~100K-300K ops/sec/node |
| Max key size | 512MB |
| Max value size | 512MB |
| Hash slots (cluster) | 16,384 |
| Practical node memory | 25-100GB |

## Redis vs Memcached (One-liner)
> "I'd use Redis here because we need [specific feature: sorted sets / persistence / pub/sub / etc.]. If it were purely a simple cache layer with no feature requirements, Memcached would be slightly more memory-efficient, but Redis is the safer default."

---

**Bottom line:** Reach for Redis when you need low-latency reads, caching, ephemeral data, counters, or ranking. Avoid it as a primary data store, for huge datasets that don't fit in memory, or when you need strong consistency.
