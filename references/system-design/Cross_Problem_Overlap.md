# Cross-Problem Overlap: Distributed Counter, Autocomplete, Calendar

**Purpose:** Identify shared patterns across system design problems to build transferable intuition.

---

## Shared Across All Three

- **Kafka as a write buffer/event bus** - Counter uses it to decouple ingestion from DB writes. Autocomplete uses it to log queries for offline aggregation. Calendar uses it for async notifications and sync.
- **Redis as a cache layer** - Counter caches counts. Autocomplete caches trie results. Calendar caches calendar views and free/busy blocks. All use cache-aside.
- **Workers consuming from a queue** - Counter has aggregation workers. Autocomplete has aggregation workers that rebuild the trie. Calendar has reminder workers and notification workers.
- **Eventual consistency is acceptable** - Counter reads tolerate staleness. Autocomplete suggestions are minutes behind. Calendar sync is near-real-time but not instant.

---

## Pairwise Overlap

### Counter + Autocomplete (but not Calendar)
- **Write-heavy, batch processing** - Both deal with high-volume event streams that get aggregated offline rather than processed individually.
- **In-memory buffering/aggregation** - Counter buffers locally before flushing. Autocomplete aggregates query frequencies in windows.
- **Cassandra / NoSQL for storage** - Simple access patterns, horizontal scaling.

### Calendar + Autocomplete (but not Counter)
- **Personalization** - Autocomplete blends personal history with global results. Calendar is inherently per-user.
- **Multiple services / microservice split** - Both have distinct services (Event/Query/Notification/Sync vs Autocomplete/UserHistory/TrieBuilder).

### Calendar + Counter (but not Autocomplete)
- **Dedup / conflict prevention** - Calendar uses DB transactions to prevent double-booking. Counter uses Redis sets to prevent double-likes. Both need to guard against invalid duplicate writes.

---

## Unique to Each

### Only Calendar
- **Strong consistency where it matters** - Conflict detection needs ACID transactions. The other two are AP systems.
- **SQL (Postgres)** - Relationships between events, attendees, recurrences. The other two use NoSQL.
- **WebSockets** - Real-time multi-device sync.

### Only Autocomplete
- **Trie as core data structure** - Specialized prefix-search structure, pre-computed top-K at each node.
- **Client-side optimizations** - Debounce, local cache, prefetch. The other two are purely server-side.

### Only Counter
- **Hot key problem** - Single viral post getting 10K writes/sec. Solved with Kafka batching or counter sharding.
- **Idempotency concerns** - Cassandra counters aren't idempotent, need batch_id pattern.

---

## The Core Takeaway

The pipeline `API -> Kafka -> Workers -> DB + Cache` appears in all three. The differences come from the requirements:

| Requirement | Drives |
|---|---|
| Consistency model (AP vs CP) | NoSQL vs SQL, eventual vs strong |
| Access patterns (key lookup vs range query vs prefix search) | DB choice and data structure |
| Read-heavy vs write-heavy | Cache strategy, buffering, replicas vs sharding |
| Real-time needs | WebSockets, Pub/Sub, polling |
| Personalization | Per-user data stores, blending strategies |

**In an interview:** Once you recognize which of these requirements apply, the architecture assembles itself from the same building blocks.

---

## Side-by-Side Component Comparison

| Component | Calendar | Like Counter | URL Shortener | Rate Limiter |
|---|---|---|---|---|
| Entry point | API Gateway | LB | LB + API Gateway | API Gateway |
| Core service | Event Service | API Server | API Server | API Gateway itself |
| Primary DB | Postgres | Cassandra | DynamoDB | Redis |
| Cache | Redis (calendar views) | Redis (like counts) | Redis (short URL mappings) | Redis (counters) |
| Async queue | Kafka | Kafka | - | - |
| Workers | Invite + Notification | Counter Workers | - | - |

## The Universal Skeleton

```
Client -> Gateway -> Service -> DB
                        |
                        v
                      Cache (read path)
                        |
                        v
                      Kafka -> Workers (when async processing needed)
```

**What changes per problem:**
- **SQL vs NoSQL** - driven by relationships and consistency needs
- **Whether you need Kafka** - driven by write volume or async work
- **What the workers do** - batch writes, send notifications, build indexes
- **Cache strategy** - cache-aside, write-through, TTL duration

Once you internalize this skeleton, every new problem is just "which pieces do I need and why."
