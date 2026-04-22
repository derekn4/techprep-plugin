# Cassandra & DynamoDB Crash Course for System Design

---

## Apache Cassandra

### What It Is
Distributed, wide-column NoSQL database designed for massive write-heavy workloads with high availability and no single point of failure. Built by Facebook, inspired by Amazon's Dynamo (distribution) + Google's Bigtable (data model).

### Architecture
- **Peer-to-peer** – no master node, every node is equal (leaderless)
- **Ring topology** – data distributed across nodes using consistent hashing
- **Gossip protocol** – nodes communicate cluster state to each other
- **Vnodes (virtual nodes)** – each physical node owns multiple token ranges for better load balancing

### Data Model
- **Keyspace** → **Table** → **Rows** → **Columns**
- **Partition key** – determines which node stores the data (hashed to a token)
- **Clustering key** – determines sort order within a partition
- **Primary key = partition key + clustering key(s)**
- **Denormalization is expected** – model tables around your queries, not entities
- No joins, no subqueries, limited aggregations

### Read/Write Path
- **Write path:** Client → Coordinator node → Commit log (sequential disk) → Memtable (memory) → SSTable (disk flush). Writes are very fast.
- **Read path:** Memtable + SSTables → merge + filter via bloom filters → return result. Reads are slower than writes.
- **Compaction** – periodically merges SSTables to reclaim space and improve read performance (strategies: Size-Tiered, Leveled, Time-Window)

### Consistency (Tunable)
- **ANY** – write to any node including hints (lowest consistency)
- **ONE/TWO/THREE** – respond after N replicas acknowledge
- **QUORUM** – majority of replicas (⌊N/2⌋ + 1)
- **ALL** – all replicas must respond (strongest, slowest)
- **Formula:** `R + W > N` for strong consistency (e.g., QUORUM reads + QUORUM writes with RF=3)
- Default is eventual consistency; tune per query

### Replication
- **Replication factor (RF)** – number of copies per partition (typically 3)
- **Replication strategies:** SimpleStrategy (single DC), NetworkTopologyStrategy (multi-DC, specify RF per datacenter)
- Multi-datacenter replication is a first-class feature

### Performance
- **Write latency:** < 1ms typical (append-only, no read-before-write)
- **Read latency:** 1–10ms typical (depends on data model and compaction)
- **Throughput:** Scales linearly – add nodes, get proportional throughput
- Handles millions of ops/sec at scale

### Key Features
- **Multi-DC / multi-region** replication built-in
- **Lightweight transactions (LWT)** – Paxos-based CAS (compare-and-set), but expensive (~4x latency)
- **TTL per column** – automatic data expiration
- **Materialized views** – auto-maintained denormalized views (use cautiously, can cause issues)
- **CDC (Change Data Capture)** – stream mutations for downstream processing
- **Time-series optimized** – Time-Window Compaction Strategy

### Limitations
- **Query-driven data model** – must know access patterns upfront; changing queries = new tables
- **No joins or complex queries** – all denormalized
- **Reads are slower than writes** – not ideal for read-heavy random lookups
- **LWT is expensive** – don't rely on it for high-throughput operations
- **Operational overhead** – tuning compaction, repairs, monitoring gc_grace_seconds
- **Tombstone accumulation** – deletes create tombstones that degrade read performance until compaction
- **No strong consistency by default** – must explicitly configure quorum reads/writes

---

## Amazon DynamoDB

### What It Is
Fully managed, serverless NoSQL key-value and document database by AWS. Designed for single-digit millisecond performance at any scale with zero operational overhead.

### Architecture
- **Fully managed** – AWS handles provisioning, patching, replication, backups, scaling
- **Partitioning** – automatic hash-based partitioning across AWS infrastructure
- **Storage nodes** – data replicated across 3 AZs automatically within a region

### Data Model
- **Table** → **Items** (rows) → **Attributes** (columns)
- **Partition key (hash key)** – determines partition placement
- **Sort key (range key)** – optional, enables range queries within a partition
- **Primary key = partition key** or **partition key + sort key (composite)**
- Schema-less (except for primary key) – each item can have different attributes
- **Item size limit: 400KB**

### Indexes
- **Local Secondary Index (LSI)** – same partition key, different sort key. Must be created at table creation. Shares throughput with base table.
- **Global Secondary Index (GSI)** – different partition key and/or sort key. Can be added anytime. Has its own throughput. Eventually consistent only.
- Max 5 LSIs, 20 GSIs per table

### Capacity Modes
- **Provisioned** – you set read/write capacity units (RCU/WCU). Cheaper if predictable traffic. Auto-scaling available.
- **On-demand** – pay per request. No capacity planning. ~6x more expensive per request but zero wasted capacity.
- Can switch between modes

### Capacity Units
- **1 RCU** = 1 strongly consistent read/sec (up to 4KB) or 2 eventually consistent reads/sec
- **1 WCU** = 1 write/sec (up to 1KB)
- Larger items consume more units proportionally

### Consistency
- **Eventually consistent** (default) – reads may not reflect latest write (~ms lag)
- **Strongly consistent** – reads guaranteed to reflect all prior writes (2x RCU cost, only available on base table and LSI)
- **No tunable consistency** – just these two options

### Performance
- **Read/Write latency:** Single-digit milliseconds (typically 1–5ms)
- **Throughput:** Virtually unlimited (scales horizontally under the hood)
- Consistent performance regardless of table size

### Key Features
- **DynamoDB Streams** – ordered stream of item changes (insert/update/delete). Powers event-driven architectures, CDC. Retention: 24 hours.
- **Global Tables** – multi-region, active-active replication with eventual consistency
- **DAX (DynamoDB Accelerator)** – in-memory cache layer, microsecond read latency
- **TTL** – automatic item expiration at no cost
- **Transactions** – ACID transactions across up to 100 items/4MB (2x cost)
- **PartiQL** – SQL-compatible query language (convenience layer, same underlying limitations)
- **Backup** – on-demand and continuous (point-in-time recovery, 35-day window)
- **Encryption at rest** – enabled by default

### Limitations
- **400KB item size limit**
- **Query flexibility is limited** – must query by primary key; GSIs needed for other access patterns
- **GSI eventual consistency only** – can't do strongly consistent reads on GSIs
- **Hot partition problem** – uneven key distribution = throttling (mitigate with key design)
- **Cost at high scale** – can get very expensive with on-demand mode or heavy GSI usage
- **AWS vendor lock-in** – proprietary service
- **No cross-item queries without indexes** – scans are expensive (reads entire table)
- **Transaction limits** – 100 items / 4MB per transaction

---

## Head-to-Head Comparison

| Dimension | Cassandra | DynamoDB |
|---|---|---|
| **Managed** | Self-managed (or DataStax Astra) | Fully managed (serverless) |
| **Ops overhead** | High (tuning, repairs, monitoring) | Near zero |
| **Cost model** | Infrastructure (EC2/hardware) | Pay-per-request or provisioned RCU/WCU |
| **Write performance** | Excellent (sub-ms) | Great (single-digit ms) |
| **Read performance** | Good (1–10ms) | Great (1–5ms, microseconds with DAX) |
| **Consistency** | Tunable (ANY → ALL) | Eventually or strongly consistent (2 options) |
| **Multi-region** | Built-in multi-DC replication | Global Tables (active-active) |
| **Max item size** | ~2GB (practical: MBs) | 400KB |
| **Query flexibility** | CQL (limited but more flexible than DDB) | Primary key + GSI only |
| **Transactions** | LWT (expensive Paxos) | ACID transactions (2x cost, 100 item limit) |
| **Vendor lock-in** | None (open source) | AWS only |
| **Scaling** | Manual (add nodes) | Automatic |
| **Best throughput** | Linear with nodes (millions ops/sec) | Virtually unlimited |

---

## When to Choose Cassandra

- **Multi-cloud or on-prem** – no vendor lock-in, runs anywhere
- **Write-heavy workloads** – time-series, IoT, logging (writes are cheaper than reads)
- **Need tunable consistency** – fine-grained control per query
- **Multi-datacenter replication** – first-class multi-DC support with full control
- **Large items** – no 400KB limit
- **Cost optimization at massive scale** – cheaper than DynamoDB when you have the team to operate it
- **You have a strong ops team** – comfortable managing distributed systems

## When to Choose DynamoDB

- **AWS-native architecture** – tight integration with Lambda, Streams, S3, etc.
- **Zero ops tolerance** – small team, no desire to manage infrastructure
- **Unpredictable traffic** – on-demand mode handles spikes automatically
- **Need microsecond reads** – DAX caching layer
- **Serverless architectures** – natural fit with Lambda + API Gateway
- **Faster time-to-market** – no cluster setup, just create a table and go
- **Moderate scale** – simpler and cheaper at small-to-medium scale
- **Need ACID transactions** – DynamoDB transactions are simpler than Cassandra LWT

## Decision Shortcut

```
Need multi-cloud or on-prem?          → Cassandra
AWS-only and want zero ops?           → DynamoDB
Write-heavy (IoT, time-series, logs)? → Cassandra (slight edge)
Serverless / Lambda-driven?           → DynamoDB
Small team, fast shipping?            → DynamoDB
Massive scale, cost-sensitive?        → Cassandra (if you can operate it)
Need tunable consistency?             → Cassandra
Items > 400KB?                        → Cassandra
```

---

## Quick Numbers

| Metric | Cassandra | DynamoDB |
|---|---|---|
| Write latency | < 1ms | 1–5ms |
| Read latency | 1–10ms | 1–5ms (μs with DAX) |
| Max item size | ~2GB | 400KB |
| Replication | Configurable RF (typically 3) | 3 AZs automatic |
| Typical RF | 3 | 3 (fixed) |
| Consistency | Tunable (ANY → ALL) | Eventual or Strong |

---

**Bottom line:** Choose DynamoDB for simplicity, serverless, and AWS-native workloads. Choose Cassandra for multi-cloud, write-heavy workloads, large items, and when you need full control over your data layer and can invest in operations.
