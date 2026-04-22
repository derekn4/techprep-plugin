# Step 2: Non-Functional Requirements - SCALED

> **Goal:** Understand how well the system needs to perform. ~2 minutes.

---

## The Checklist

- **S** - Scalability (how many users, how much data, read-heavy or write-heavy?)
- **C** - Consistency (strong vs eventual? what data can't be stale?)
- **A** - Availability (can the system go down? what's the uptime target?)
- **L** - Latency (how fast do responses need to be?)
- **E** - Else (security, compliance, anything problem-specific)
- **D** - Durability / Fault Tolerance (can we lose data? what happens when things break?)

---

## Target: 2-3 Clarifying Questions, Prioritize S and C

- **Scalability** (1 question, always ask): "How many users? Is this read-heavy or write-heavy?" - drives half your architecture.
- **Consistency** (1 question, usually ask): "Does this need strong consistency or is eventual OK?" - determines your DB/cache strategy. Remember: consistency = "do all users see the same thing right now?" (not "is the data safe" -- that's durability).
- **Latency** (1 question, if relevant): "What's the latency target?" - matters for real-time systems, less so for batch/async.
- Skip A, E, D unless the problem calls for them. Availability is almost always "yes, high availability" (not worth asking). Durability is almost always "yes, don't lose data." Else is for unusual requirements.

---

## Consistency vs Durability (Don't Confuse These)

- **Consistency** = How quickly do all users/replicas see the **latest** data? **OR** "Do all users see the same thing right now?"
- **Durability** = Is the data **safe** after a crash/failure? **OR** "Is the data still there after a crash?"

A system can be durable but inconsistent (data is safe on disk, but replicas are out of sync for a few seconds). And consistent but not durable (everyone sees the same value, but it's only in memory and a crash kills it).

**"What about accuracy?"** -- Accuracy isn't its own NFR. It maps to one of two questions:
- "Can we show stale data?" -- that's **Consistency (C)**. Eventual consistency = briefly inaccurate reads.
- "Can we show approximate data?" -- that's **Else (E)**. Things like HyperLogLog (~98% accurate) or approximate counters. You're choosing to sacrifice precision for performance.

---

## Strong vs Eventual Consistency: What It Means for Your Design

| | Write path | Read path | Cache strategy | Tradeoff |
|---|---|---|---|---|
| **Strong** | Write to DB + cache atomically | Read from cache or DB (both are guaranteed fresh) | Write-through (every write updates DB and cache together). Cache is never stale, so reads can safely hit cache. | Slower writes (dual write), always correct reads |
| **Eventual** | Write to DB, cache updates lazily | Read from cache or read replica (might be briefly stale) | Cache-aside, write-back, or TTL-based expiry. Cache may be stale for a short window. | Faster reads, briefly stale |

**The key invariant for strong consistency:** A read never returns stale data. That doesn't mean you must read from DB -- it means whatever you read from must be guaranteed fresh. Write-through cache achieves this. Reading directly from DB is just the simplest way.

**Cache strategies (from simplest to most complex):**
- **Cache-aside / lazy-loading** (eventual): Read cache -> miss -> read DB -> populate cache -> return. Between a write to DB and the next cache miss or TTL expiry, readers see stale data. Most common pattern for eventual consistency. No write-side cache logic needed.
- **Invalidate on write** (strong): Delete the cache key when you write to DB. Next read misses cache, fetches fresh from DB, repopulates cache. Simple and safe, but the first read after a write is slower (cache miss).
- **Write-through** (strong): Write to DB and cache atomically on every write. Cache is always fresh, so reads are always fast. More complex writes, but guarantees strong consistency from cache.
- **Write-back / write-behind** (eventual): Write to cache first, async flush to DB later. Fastest writes, but risk of data loss if cache crashes before flush. Rarely used for critical data.
- **TTL-based expiry** (eventual): Cache entries expire after N seconds. Stale for up to N seconds, but zero write-side complexity. Good for data where "close enough" is fine (profiles, feeds, dashboards).

**One-liner:** Strong = always read from the thing you write to (unless cache is guaranteed fresh via write-through). Eventual = read from a fast copy that catches up.

**When each matters:**
- **Strong:** Money, inventory, seat reservations -- stale = wrong behavior
- **Eventual:** Feeds, likes, notifications, analytics -- briefly stale is fine
