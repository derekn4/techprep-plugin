# Memcached Crash Course for System Design

## What It Is
Distributed, in-memory key-value cache. Pure caching layer — simpler than Redis, laser-focused on speed. No persistence, no fancy data structures, just blazing fast get/set.

## Performance
- **Read/Write latency:** sub-millisecond (~100–500 microseconds)
- **Throughput:** ~200K–1M+ ops/sec per node (higher than Redis for simple ops due to multithreading)
- **Why so fast:** In-memory, multithreaded architecture, simple key-value model with minimal overhead

## Data Model
- **Keys:** up to 250 bytes
- **Values:** up to 1MB (default), raw bytes/strings only
- **No data structures** — no lists, sets, sorted sets, etc. Just `get`, `set`, `delete`, `incr/decr`
- Supports **CAS (Check-And-Set)** for optimistic concurrency

## Architecture

### Multithreaded
- Unlike Redis (single-threaded for commands), Memcached is **multithreaded** out of the box
- Scales vertically with CPU cores on a single machine
- This is its main advantage over Redis for pure caching workloads

### Client-Side Sharding (Distributed Hashing)
- Memcached servers **don't talk to each other** — no clustering protocol
- The **client** decides which server to route to using **consistent hashing**
- Adding/removing nodes only remaps ~1/N of keys (vs. naive hashing which remaps almost everything)
- No built-in replication, failover, or coordination between nodes

### Memory Management — Slab Allocation
- Memory pre-divided into **slab classes** of fixed chunk sizes (64B, 128B, 256B, etc.)
- Items stored in the smallest slab class that fits
- **Pros:** No memory fragmentation, O(1) allocation
- **Cons:** Internal fragmentation (a 65-byte item uses a 128-byte chunk), slab calcification (uneven slab distribution over time)

## Eviction
- **LRU per slab class** — when a slab is full, least recently used item in that slab gets evicted
- No TTL-based eviction scan — expired items are evicted lazily (on access or when space is needed)
- No configurable eviction policies like Redis — it's LRU or nothing

## Expiration
- TTL-based expiration on keys
- Max TTL: 30 days (values > 30 days are treated as Unix timestamps)
- Lazy expiration — items aren't actively removed, just ignored when accessed after expiry

## No Persistence
- **Purely ephemeral** — server restarts = all data gone
- This is by design. It's a cache, not a database.
- If you need persistence, use Redis instead

## No Replication
- No built-in master-replica replication
- If a node dies, that data is just gone — clients re-route and cache misses hit the database
- Some deployments use **mcrouter** (Facebook's proxy) to add replication, connection pooling, and routing logic

## Scaling
- **Horizontal:** Add more nodes, client consistent hashing redistributes keys
- **Vertical:** Add more RAM and CPU cores (multithreaded)
- Nodes are completely independent — simple to operate

## Common System Design Use Cases

| Use Case | How |
|---|---|
| **Database query cache** | Cache DB results, TTL-based invalidation |
| **Session store** | Simple, fast session lookups (but no persistence — be aware) |
| **Page/fragment caching** | Cache rendered HTML fragments |
| **API response caching** | Store serialized API responses |
| **Simple counters** | INCR/DECR for rate limiting or counting |
| **Hot data offload** | Protect DB from thundering herd |

## Memcached vs Redis — When to Use Which

| Factor | Memcached | Redis |
|---|---|---|
| **Data structures** | Strings only | Strings, lists, sets, sorted sets, hashes, streams, etc. |
| **Threading** | Multithreaded | Single-threaded (I/O threads in 6+) |
| **Persistence** | None | RDB, AOF |
| **Replication** | None built-in | Master-replica |
| **Eviction** | LRU only | LRU, LFU, random, volatile, etc. |
| **Max value size** | 1MB | 512MB |
| **Use case** | Simple, high-throughput caching | Caching + data structures + pub/sub + more |
| **Operational complexity** | Very simple | More features = more knobs |

**TL;DR:** Use Memcached when you need a simple, multithreaded, high-throughput cache with no bells and whistles. Use Redis when you need data structures, persistence, replication, or pub/sub.

## Key Limitations to Mention in Interviews
- **No persistence** — pure cache, data is ephemeral
- **No replication** — node failure = cache miss storm (cold cache problem)
- **No data structures** — just strings/bytes
- **1MB value limit** — can be restrictive for large objects
- **No built-in clustering** — client handles distribution
- **Slab fragmentation** — memory waste if item sizes vary a lot
- **No pub/sub, no scripting, no transactions**

## Quick Numbers to Remember

| Metric | Value |
|---|---|
| Latency | < 1ms (~100-500μs) |
| Throughput | ~200K-1M+ ops/sec/node |
| Max key size | 250 bytes |
| Max value size | 1MB (default) |
| Threading | Multithreaded |
| Persistence | None |
| Replication | None (built-in) |

---

**Bottom line:** Memcached is the go-to when you need a dead-simple, high-performance distributed cache. It does one thing and does it extremely well. Choose it over Redis when you don't need data structures, persistence, or replication — just raw caching speed.
