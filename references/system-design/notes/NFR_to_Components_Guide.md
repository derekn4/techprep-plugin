# Non-Functional Requirements → System Design Components

> **How to use this:** When the interviewer states a non-functional requirement, use this guide to
> quickly identify which components, patterns, and technologies to reach for and WHY.

---

## Master Lookup Table

| NFR | Reach For | Why |
|-----|-----------|-----|
| **High Read Throughput** | Cache (Redis/Memcached), Read Replicas, CDN | Offload reads from primary DB; serve from memory instead of disk |
| **High Write Throughput** | Message Queue (Kafka), Write-behind cache, LSM-tree DBs (Cassandra), Sharding | Buffer writes async; use append-only storage; spread writes across nodes |
| **Low Read Latency** | Cache, CDN, Denormalized data, In-memory DB (Redis) | Eliminate disk I/O; serve from edge/memory; avoid JOINs at read time |
| **Low Write Latency** | Append-only logs, Write-ahead log, Async processing (queues) | Acknowledge fast, process later; sequential writes are faster than random |
| **Strong Consistency** | SQL (Postgres/MySQL), Single-leader replication, Consensus (Raft/Paxos), Transactions | One source of truth; all reads see latest write; ACID guarantees |
| **Eventual Consistency** | NoSQL (Cassandra/DynamoDB), Multi-leader replication, CRDTs, Queues | Accept temporary staleness for higher availability and partition tolerance |
| **High Availability** | Multi-region deployment, Replication, Load balancers, Health checks, Failover | No single point of failure; if one node dies, others pick up traffic |
| **Durability** | WAL, Replication (3+ copies), S3/Blob storage, Backups | Data survives crashes; multiple copies across nodes/regions |
| **Horizontal Scalability** | Stateless services, Sharding, Consistent hashing, Load balancers | Add more machines instead of bigger machines; distribute load evenly |
| **Real-Time Updates** | WebSockets, SSE, Pub/Sub (Redis Pub/Sub, Kafka) | Push data to clients immediately; avoid polling overhead |
| **Search / Query Flexibility** | Elasticsearch, Inverted index, Denormalized read models | Full-text search, fuzzy matching, faceted queries - things SQL can't do well |
| **Analytics / Aggregation** | Data warehouse (BigQuery/Redshift), OLAP DB, Batch processing (Spark) | Separate read path for heavy aggregations; don't slow down production DB |
| **Fault Tolerance** | Circuit breakers, Retries with backoff, Dead letter queues, Bulkheads | Graceful degradation; failures don't cascade; failed work isn't lost |
| **Global / Low Latency Worldwide** | CDN, Multi-region, Geo-routing (DNS-based), Edge computing | Serve users from nearest data center; reduce network round-trip time |
| **Rate Limiting / Abuse Prevention** | API Gateway, Token bucket / Sliding window, Redis counters | Protect backend from overload; fair usage across users |

---

## Detailed Breakdowns

### 1. High Read Throughput / Read-Heavy Systems

**Scenario:** "We expect 100:1 read-to-write ratio" or "Millions of users reading feeds/profiles"

```
                         ┌──────────┐
          ┌─────────────►│  CDN     │  (static assets, images)
          │              └──────────┘
          │
 Client ──┤              ┌──────────┐     ┌──────────────┐
          ├─────────────►│  Cache   │────►│ Read Replica  │
          │              │ (Redis)  │     │  (Postgres)   │
          │              └──────────┘     └──────────────┘
          │                                      │
          │                               ┌──────┴──────┐
          └──────────────────────────────►│Primary DB    │
                    (cache miss path)     │(writes only) │
                                          └─────────────┘
```

**Components to mention:**
- **Cache layer (Redis/Memcached)** - Store hot data in memory. Cache hit = microseconds vs milliseconds from DB.
- **Read replicas** - Multiple DB copies handle reads. Primary handles writes only.
- **CDN** - For static content (images, JS, CSS). Serve from edge, not origin.
- **Denormalization** - Pre-join data at write time so reads don't need JOINs.

**Tradeoff to articulate:** "We're trading write complexity for read speed. Writes need to update the cache and denormalized views, but reads are now O(1) lookups."

---

### 2. High Write Throughput / Write-Heavy Systems

**Scenario:** "Logging system ingesting 1M events/sec" or "IoT sensor data from millions of devices"

```
 Producers ──► Message Queue (Kafka) ──► Consumer Workers ──► Database
                  (buffer + order)        (batch writes)     (LSM-tree/
                                                              append-only)
```

**Components to mention:**
- **Message queue (Kafka/SQS)** - Buffer incoming writes. Producers get fast ack. Consumers process at their own pace.
- **LSM-tree databases (Cassandra, HBase, LevelDB)** - Optimized for writes. Append-only in memory, flush to disk periodically.
- **Sharding / Partitioning** - Distribute writes across multiple DB nodes. Each shard handles a subset.
- **Write-behind cache** - Write to cache first (fast), flush to DB in batches (efficient).
- **Batch processing** - Group many small writes into fewer large writes.

**Tradeoff to articulate:** "We're trading read efficiency for write speed. LSM-trees are slower for point reads (need to check multiple levels), but writes are nearly sequential I/O which is extremely fast."

---

### 3. Low Latency (Read or Write)

**Scenario:** "Sub-10ms response time" or "Real-time trading system"

**For low READ latency:**
- **In-memory cache (Redis)** - Microsecond reads vs millisecond disk reads
- **CDN / Edge caching** - Reduce network hops
- **Denormalized data** - Avoid JOINs at query time
- **Connection pooling** - Avoid TCP handshake overhead per request
- **Pre-computed results** - Materialize views ahead of time

**For low WRITE latency:**
- **Write-ahead log (WAL)** - Ack after writing to log (sequential), apply to DB later
- **Async processing** - Ack immediately, push work to queue
- **In-memory writes** - Write to Redis first, persist later (risk: data loss on crash)
- **Batching** - Group writes together (tradeoff: slightly higher latency per individual write, but higher throughput)

**Key insight to mention:** "There's a fundamental tension between latency and durability. Writing to memory is fast but volatile. Writing to disk is durable but slower. WAL gives us both: fast sequential disk write for durability, then apply at leisure."

---

### 4. Strong Consistency

**Scenario:** "Bank account balances" or "Inventory counts" or "Exactly-once payments"

**Components to mention:**
- **SQL database (Postgres/MySQL)** - ACID transactions, serializable isolation
- **Single-leader replication** - All writes go through one node, reads from same node
- **Consensus protocols (Raft/Paxos)** - For distributed systems that need agreement (e.g., etcd, ZooKeeper)
- **Distributed transactions** - Two-phase commit (2PC) when data spans services
- **Optimistic locking / CAS** - Compare-and-swap for concurrent updates without heavy locks

**Tradeoff to articulate (CAP theorem):** "Strong consistency means we sacrifice some availability. During a network partition, we'll reject writes rather than risk inconsistent data. For financial transactions, that's the right tradeoff."

---

### 5. Eventual Consistency

**Scenario:** "Social media likes count" or "User activity feed" or "Product recommendations"

**Components to mention:**
- **NoSQL databases (Cassandra, DynamoDB)** - Tunable consistency (ONE, QUORUM, ALL)
- **Multi-leader / leaderless replication** - Multiple nodes accept writes independently
- **CRDTs (Conflict-free Replicated Data Types)** - Data structures that auto-merge without coordination (counters, sets)
- **Message queues for async sync** - Changes propagate through events
- **Last-write-wins (LWW)** - Simplest conflict resolution (timestamp-based)

**Tradeoff to articulate:** "Eventual consistency gives us higher availability and lower latency because any node can accept writes. The cost is that two users might briefly see different values. For a like count, that's perfectly acceptable."

---

### 6. High Availability (99.99%+)

**Scenario:** "System must never go down" or "Health-critical application"

```
                    ┌─────────────┐
         ┌────────►│  Region A    │
         │          │ (Primary)   │
 Users ──┤          └──────┬──────┘
 (DNS    │                 │ replication
 routing)│          ┌──────▼──────┐
         └────────►│  Region B    │
                    │ (Standby)   │
                    └─────────────┘
```

**Components to mention:**
- **Multi-region deployment** - Survive entire data center failures
- **Load balancers with health checks** - Route away from unhealthy instances automatically
- **Replication (sync or async)** - Data exists in multiple places
- **Auto-scaling** - Handle traffic spikes without manual intervention
- **Failover mechanisms** - Automatic promotion of standby to primary
- **Graceful degradation** - Serve cached/stale data rather than errors

**Tradeoff to articulate:** "High availability in a distributed system means we may need to relax consistency (CAP theorem). During a partition, we serve potentially stale data rather than returning errors. We can use techniques like read-your-writes consistency to minimize user-visible staleness."

---

### 7. Durability (Never Lose Data)

**Scenario:** "Financial records" or "Medical data" or "User-generated content"

**Components to mention:**
- **Write-ahead log (WAL)** - Log the change before applying it. Recover from crash by replaying log.
- **Replication factor of 3+** - Data exists on at least 3 nodes across failure domains
- **S3 / Blob storage** - 99.999999999% (11 nines) durability for objects
- **Backups (incremental + full)** - Point-in-time recovery capability
- **Checksums** - Detect bit rot and corruption

**Tradeoff to articulate:** "More durability means more write latency (need to confirm writes to multiple replicas) and more storage cost. For critical data, that cost is justified. For ephemeral data like session tokens, a single copy in Redis is fine."

---

### 8. Horizontal Scalability

**Scenario:** "System needs to handle 10x growth" or "From 1K to 1M users"

**Components to mention:**
- **Stateless application servers** - Any server can handle any request. Scale by adding servers.
- **Database sharding** - Partition data across DB nodes (by user_id, geo, hash)
- **Consistent hashing** - Distribute data evenly; minimize redistribution when adding/removing nodes
- **Load balancers** - Distribute traffic across application instances
- **Service decomposition** - Break monolith into services that scale independently
- **Shared-nothing architecture** - Each node is self-sufficient

**Key sharding strategies to know:**

| Strategy | How It Works | Good For | Watch Out For |
|----------|-------------|----------|---------------|
| Hash-based | hash(key) % N | Even distribution | Adding nodes reshuffles data (use consistent hashing) |
| Range-based | key ranges per shard | Range queries | Hot spots if ranges uneven |
| Geo-based | region per shard | Locality | Cross-region queries are expensive |
| Directory-based | Lookup table maps key to shard | Flexible | Lookup table is single point of failure |

---

### 9. Real-Time Updates

**Scenario:** "Live chat" or "Collaborative editing" or "Live sports scores"

**Decision tree:**
```
Does the CLIENT need to send data too?
    ├── YES (bidirectional) ──► WebSockets
    │       Examples: Chat, multiplayer games, collaborative editing
    │
    └── NO (server push only) ──► SSE (Server-Sent Events)
            Examples: Live dashboards, notifications, score updates
```

**Supporting infrastructure:**
- **Pub/Sub layer (Redis Pub/Sub or Kafka)** - Fan out messages across multiple WebSocket server instances
- **Connection registry** - Track which user is connected to which server
- **Presence service** - Track online/offline status
- **Message ordering** - Sequence numbers or vector clocks

---

## Common NFR Combinations (Interview Patterns)

These combinations appear repeatedly. Knowing the pattern saves time:

### Pattern A: Social Media Feed (Read-heavy + Eventual Consistency + Low Read Latency)
```
Write path: User posts → Queue → Fan-out service → Write to follower feeds (denormalized)
Read path:  User opens app → Cache (Redis) → Pre-built feed → Fast response
```
- **Fan-out on write** for users with few followers (pre-compute feeds)
- **Fan-out on read** for celebrities (compute at read time to avoid writing to millions of feeds)
- Cache the feed, eventual consistency is fine (a few seconds delay on new posts is acceptable)

### Pattern B: E-Commerce / Payments (Strong Consistency + Durability + High Availability)
```
Write path: Order placed → SQL DB (ACID transaction) → Replicated (sync) → Queue → Fulfillment
Read path:  Product catalog → Cache + Read replicas (can be eventually consistent)
```
- Strong consistency for orders/payments/inventory (ACID transactions, no double-spending)
- Eventual consistency is fine for product catalog, reviews, recommendations
- **Split the consistency model** by data type

### Pattern C: Logging / Metrics (High Write Throughput + Eventual Consistency + Analytics)
```
Write path: Events → Kafka (buffer) → Consumers → Time-series DB or Data warehouse
Read path:  Dashboard → Pre-aggregated tables → Cached results
```
- Append-only, never update
- Batch writes for efficiency
- Pre-aggregate for fast dashboard reads

### Pattern D: Chat / Messaging (Real-Time + Durability + Ordering)
```
Write path: Message → WebSocket server → Kafka (ordered by conversation) → DB
Read path:  Recent messages from cache, older messages from DB (paginated)
```
- WebSockets for real-time delivery
- Kafka for message ordering and durability
- Cache recent conversation history

### Pattern E: URL Shortener / Key-Value Store (High Read + Low Latency + Scalability)
```
Write path: Create short URL → Generate ID → Write to DB (sharded by hash)
Read path:  Redirect → Cache lookup (Redis) → DB fallback → 301 redirect
```
- Heavy caching (URLs rarely change after creation)
- Consistent hashing for even distribution across shards
- Read-through cache pattern

---

## Quick Decision Tables

### Database Selection

| If you need... | Use | Why |
|----------------|-----|-----|
| ACID transactions, complex queries, JOINs | **PostgreSQL / MySQL** | Relational model, strong consistency |
| High write throughput, horizontal scale | **Cassandra** | LSM-tree, tunable consistency, masterless |
| Flexible schema, document storage | **MongoDB** | JSON documents, good for evolving schemas |
| Key-value with low latency | **Redis / DynamoDB** | In-memory (Redis) or managed (Dynamo), sub-ms reads |
| Graph relationships (social, recommendations) | **Neo4j** | Optimized for traversals and relationship queries |
| Full-text search | **Elasticsearch** | Inverted index, fuzzy matching, relevance scoring |
| Time-series data (metrics, IoT) | **InfluxDB / TimescaleDB** | Optimized for time-ordered append-heavy workloads |
| Blob/file storage | **S3 / GCS** | Cheap, durable (11 nines), scalable object storage |

### Cache Strategy Selection

| Pattern | How It Works | Best When |
|---------|-------------|-----------|
| **Cache-aside (lazy loading)** | App checks cache first, loads from DB on miss, writes to cache | General purpose, read-heavy |
| **Write-through** | App writes to cache AND DB simultaneously | Need cache to always be fresh |
| **Write-behind** | App writes to cache, cache async flushes to DB | Write-heavy, can tolerate slight data loss risk |
| **Read-through** | Cache automatically loads from DB on miss | Want to simplify app logic |
| **Refresh-ahead** | Cache proactively refreshes before expiry | Predictable access patterns, need low latency |

### Message Queue Selection

| If you need... | Use | Why |
|----------------|-----|-----|
| High throughput, ordering, replay | **Kafka** | Log-based, partitioned, consumers can rewind |
| Simple task queue, at-least-once delivery | **SQS / RabbitMQ** | Easy setup, built-in retry/DLQ |
| Real-time pub/sub, fan-out to WebSockets | **Redis Pub/Sub** | Low latency, fire-and-forget (no persistence) |
| Exactly-once, complex routing | **RabbitMQ** | Exchange types, routing keys, acknowledgments |

---

## The "Why" Cheat Sheet

> In interviews, ALWAYS explain WHY you chose something. Here are one-liner justifications:

| Component | One-Liner "Why" |
|-----------|-----------------|
| Redis cache | "Sub-millisecond reads from memory vs. 5-10ms from disk" |
| Read replicas | "Distribute read load; primary handles writes only" |
| Kafka | "Decouples producers from consumers; handles traffic spikes; preserves message ordering" |
| CDN | "Serves static content from edge locations closest to users, reducing latency to under 50ms globally" |
| Load balancer | "Distributes traffic evenly and routes around unhealthy instances" |
| Sharding | "No single DB can handle this volume; sharding lets us scale writes horizontally" |
| WebSockets | "Bidirectional persistent connection; server can push to client without polling" |
| Consistent hashing | "When we add or remove nodes, only K/N keys need to move instead of reshuffling everything" |
| Write-ahead log | "Fast sequential write for durability, then apply to storage at leisure" |
| Circuit breaker | "Prevents cascading failures; fails fast instead of waiting on a dead service" |
| Rate limiter | "Protects backend from abuse and ensures fair usage across clients" |
| Denormalization | "Trades storage space and write complexity for faster reads by avoiding JOINs" |

---

## Interview Flow: NFR → Architecture

When you hear the NFR, follow this mental process:

```
1. HEAR the requirement
   "We need high availability and low latency for reads"

2. MAP to components (use table above)
   High availability → multi-region, replication, failover
   Low read latency  → cache, CDN, denormalized data

3. STATE your choice with WHY
   "I'd add a Redis cache in front of the database because
    we need sub-millisecond read latency, and a CDN for
    static assets to reduce latency for global users."

4. ACKNOWLEDGE the tradeoff
   "The tradeoff is cache invalidation complexity - we need
    a strategy for keeping the cache consistent with the DB.
    I'd use cache-aside with a TTL of 60 seconds, which gives
    us eventual consistency within a minute."
```

This four-step pattern (hear, map, state+why, tradeoff) makes you sound like an engineer who understands the reasoning, not just the components.
