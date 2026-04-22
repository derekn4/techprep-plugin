# Read-Heavy vs Write-Heavy: Data Access Pattern Guide

---

## Core Tradeoffs

| Optimizing For | You're Trading Away |
|---|---|
| **Reads** | More copies of data, more storage cost, more staleness risk, more sync complexity. Trading freshness and storage for speed. |
| **Writes** | Deferred consistency, risk of data loss, more complex failure handling, harder reads. Trading read simplicity and consistency for throughput. |

---

## Read-Heavy Strategies

### 01 — Cache-Aside (Lazy Loading)

**How it works:** App checks cache first → miss? Read from DB → populate cache → return.

**Best for:** Unpredictable read patterns, tolerance for cache misses on first access.

**Examples:** Redis + PostgreSQL, Memcached + MySQL

**Drawbacks:**
- First read is always a cache miss (cold start penalty)
- Cache can serve stale data if DB is updated directly
- Application owns cache logic — more code complexity
- Cache stampede risk when popular keys expire simultaneously

---

### 02 — Read-Through Cache

**How it works:** Cache sits in front of DB. On miss, cache itself fetches from DB and stores it.

**Best for:** Simpler app code, predictable access patterns.

**Examples:** AWS DAX (DynamoDB), NCache, custom proxy layer

**Drawbacks:**
- Cache library/provider must support your DB — less flexible
- Still cold-start penalty on first read
- Harder to customize fetch logic per query
- Tight coupling between cache and data source

---

### 03 — Read Replicas

**How it works:** Replicate primary DB to read-only followers. Route reads to replicas, writes to primary.

**Best for:** SQL-heavy reads, reporting/analytics, geographic distribution.

**Examples:** PostgreSQL streaming replicas, Aurora read replicas, MySQL replicas

**Drawbacks:**
- Replication lag → stale reads (seconds to minutes)
- Cannot write to replicas — read-only
- More infrastructure to manage and monitor
- Doesn't help with write bottlenecks at all

---

### 04 — CDN / Edge Caching

**How it works:** Cache responses at edge nodes geographically close to users.

**Best for:** Static assets, API responses that rarely change, global user base.

**Examples:** CloudFront, Cloudflare, Fastly, Akamai

**Drawbacks:**
- Cache invalidation is notoriously hard
- Stale content served until TTL expires
- Not suitable for personalized or frequently changing data
- Debugging cache behavior across edge nodes is painful

---

### 05 — Materialized Views / Precomputed Results

**How it works:** Precompute expensive query results and store them. Refresh on schedule or via triggers.

**Best for:** Dashboards, aggregations, complex joins that are read frequently.

**Examples:** PostgreSQL materialized views, Redis precomputed keys, Elasticsearch indices

**Drawbacks:**
- Data staleness between refreshes
- Storage overhead for precomputed data
- Refresh jobs add operational complexity
- Must anticipate query patterns in advance — inflexible

---

### 06 — CQRS (Read Model)

**How it works:** Maintain a separate, optimized read store denormalized for your query patterns.

**Best for:** Read/write patterns that diverge significantly, event-sourced systems.

**Examples:** Kafka → Elasticsearch (read), PostgreSQL (write). Event store + projections.

**Drawbacks:**
- Eventual consistency between read and write stores
- Significant architectural complexity
- Must build and maintain sync pipeline
- Debugging inconsistencies across stores is difficult

---

### 07 — Search Index

**How it works:** Sync data to inverted index for fast full-text search, filtering, and faceting.

**Best for:** Full-text search, autocomplete, complex filtering on large datasets.

**Examples:** Elasticsearch, OpenSearch, Typesense, Meilisearch

**Drawbacks:**
- Not a source of truth — sync lag from primary DB
- Resource-heavy (RAM and disk for indices)
- Cluster management is operationally complex
- Write throughput to index is limited

---

## Write-Heavy Strategies

### 01 — Write-Behind / Write-Back Cache

**How it works:** Write to cache immediately → async flush to DB in background.

**Best for:** High write bursts, acceptable small window of data loss risk.

**Examples:** Redis + async flush worker, Hazelcast write-behind

**Drawbacks:**
- Data loss risk if cache crashes before flush
- Ordering and consistency are hard to guarantee
- Complex failure handling and retry logic needed
- DB and cache can diverge silently

---

### 02 — Message Queue / Write Buffer

**How it works:** Producer writes to queue → consumers drain to DB at sustainable rate.

**Best for:** Spike absorption, decoupling producers from slow consumers.

**Examples:** Kafka, SQS, RabbitMQ → DB consumer workers

**Drawbacks:**
- Added latency — write isn't in DB immediately
- Queue can become a bottleneck or single point of failure
- Ordering guarantees add complexity (partitioning needed)
- Consumer lag monitoring and dead letter queues required

---

### 03 — Database Sharding

**How it works:** Partition data across multiple DB nodes by shard key (user_id, region, etc.).

**Best for:** Massive write volume that exceeds single-node capacity.

**Examples:** Vitess (MySQL), Citus (PostgreSQL), custom app-level sharding

**Drawbacks:**
- Cross-shard queries are expensive or impossible
- Resharding when data grows is extremely painful
- Shard key choice is critical — bad key = hot spots
- Joins across shards require application-level logic

---

### 04 — LSM Tree / Append-Only Storage

**How it works:** Writes go to in-memory buffer → flush to sorted files on disk. Optimized for sequential writes.

**Best for:** Time-series data, logs, IoT, any append-heavy workload.

**Examples:** Cassandra, RocksDB, LevelDB, HBase, ScyllaDB

**Drawbacks:**
- Read amplification — may check multiple SSTables
- Compaction causes periodic CPU/IO spikes
- Space amplification from duplicate keys pre-compaction
- Point lookups slower than B-tree based stores

---

### 05 — Batch Writes / Bulk Inserts

**How it works:** Buffer individual writes and flush as a single batch operation.

**Best for:** High-frequency small writes, ETL pipelines, log ingestion.

**Examples:** PostgreSQL COPY, Kafka batch producer, bulk Elasticsearch indexing

**Drawbacks:**
- Increased write latency for individual records
- Batch failure = all records in batch fail (need retry logic)
- Memory pressure from buffering
- Tuning batch size is a tradeoff: too small = no benefit, too large = latency

---

### 06 — Event Sourcing

**How it works:** Store every state change as an immutable event. Current state = replay of events.

**Best for:** Audit trails, undo/redo, financial systems, complex domain logic.

**Examples:** EventStoreDB, Kafka as event log, Axon Framework

**Drawbacks:**
- Event store grows unbounded — needs snapshotting
- Rebuilding current state from events can be slow
- Schema evolution of events is very tricky
- Steep learning curve — unfamiliar paradigm for most teams

---

### 07 — Multi-Leader / Leaderless Replication

**How it works:** Multiple nodes accept writes independently. Conflict resolution handles divergence.

**Best for:** Geo-distributed writes, high availability during partitions.

**Examples:** Cassandra, DynamoDB (multi-region), CockroachDB, Riak

**Drawbacks:**
- Conflict resolution is genuinely hard (LWW loses data)
- No linearizable consistency without coordination
- Debugging is a nightmare — which write won?
- CRDTs help but only for specific data structures

---

## Quick Decision Framework

| Scenario | Recommendation |
|---|---|
| Read:Write ratio > 10:1? | Cache-aside + read replicas. Covers 90% of cases. |
| Write:Read ratio > 10:1? | Message queue + LSM-tree store (Cassandra/ScyllaDB). Buffer and batch. |
| Need both high reads AND writes? | CQRS — separate stores optimized for each path. |
| Spiky write traffic? | Queue as buffer → drain at steady rate. Don't over-provision for peaks. |
| Global users, read-heavy? | CDN + regional read replicas. Push data to the edge. |
| Strong consistency + high reads? | Primary DB + cache with short TTL or invalidation on write. Accept the complexity. |

---

## Interview Tip

> Don't just say "add a cache." Specify *which* caching pattern, *where* in the stack, what the *eviction policy* is, and what happens on a *cache miss*. Similarly for writes — mention what happens if the queue goes down, how you handle backpressure, and whether you need ordering guarantees. Articulating drawbacks unprompted shows depth.
