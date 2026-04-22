# Apache Kafka Crash Course for System Design

## What It Is
Distributed event streaming platform. A durable, high-throughput, fault-tolerant commit log for publishing, subscribing to, storing, and processing streams of events in real time. Think of it as a persistent, replayable message bus.

## Performance
- **Throughput:** Millions of messages/sec per cluster (single broker can handle ~100K–200K+ msgs/sec)
- **Latency:** ~2–10ms for production to consumption (low single-digit ms in optimized setups)
- **Why so fast:** Sequential disk I/O (append-only log), zero-copy transfers, batching, page cache utilization, no random disk seeks

## Core Concepts

### Topics & Partitions
- **Topic** – a named feed/category of messages (e.g., `user-clicks`, `order-events`)
- **Partition** – a topic is split into partitions for parallelism. Each partition is an ordered, immutable append-only log.
- Messages within a partition have a sequential **offset** (unique ID)
- **Ordering is guaranteed only within a partition**, not across partitions
- Partition count is set at topic creation (can increase but not decrease)

### Producers
- Write messages to topics
- Choose partition via: round-robin (default), key-based hashing (same key → same partition → ordering), or custom partitioner
- Can configure **acks** for durability:
  - `acks=0` – fire and forget (fastest, least safe)
  - `acks=1` – leader acknowledges (default)
  - `acks=all` – all in-sync replicas acknowledge (safest, slowest)

### Consumers & Consumer Groups
- **Consumer** – reads messages from topic partitions
- **Consumer Group** – multiple consumers sharing the work. Each partition is assigned to exactly one consumer in the group.
- Scaling: add consumers up to the number of partitions (more consumers than partitions = idle consumers)
- **Offset tracking** – consumers commit offsets to track progress. Can replay by resetting offsets.

### Brokers
- Individual Kafka server nodes
- Each broker stores partitions and serves client requests
- A cluster is a group of brokers (typically 3–dozens)

## Replication & Fault Tolerance
- Each partition has a **leader** and N-1 **follower** replicas (configured by `replication-factor`, typically 3)
- All reads/writes go through the leader (followers replicate passively)
- **ISR (In-Sync Replicas)** – replicas caught up with the leader. If leader dies, a new leader is elected from ISR.
- **`min.insync.replicas`** – minimum ISR count required for `acks=all` writes to succeed (commonly set to 2 with replication-factor=3)
- **Unclean leader election** – allow out-of-sync replica to become leader (trades durability for availability)

## Kafka's Controller / Coordination

### ZooKeeper (Legacy)
- Managed broker metadata, leader election, topic configs
- Being phased out

### KRaft (Kafka Raft – New)
- Built-in consensus protocol replacing ZooKeeper
- Metadata managed by a quorum of controller nodes within the Kafka cluster itself
- Simpler architecture, faster startup, better scalability

## Message Retention
- **Time-based** – retain messages for X hours/days (default 7 days)
- **Size-based** – retain up to X bytes per partition
- **Compacted topics** – keep only the latest value per key (great for changelogs, state snapshots)
- Messages are NOT deleted after consumption – multiple consumers can read independently

## Delivery Semantics
| Semantic | How |
|---|---|
| **At-most-once** | Commit offset before processing. May lose messages. |
| **At-least-once** | Commit offset after processing. May get duplicates. (Default) |
| **Exactly-once** | Idempotent producers + transactional API. Higher overhead. |

## Kafka Streams
- Lightweight stream processing library (runs inside your app, no separate cluster)
- Supports stateful operations: joins, aggregations, windowing
- Backed by internal Kafka topics for state stores
- Good for: real-time transformations, enrichment, simple stream processing

## Kafka Connect
- Framework for pluggable **source connectors** (DB → Kafka) and **sink connectors** (Kafka → DB/S3/Elasticsearch/etc.)
- Handles offset tracking, scaling, fault tolerance automatically
- Avoids writing custom producer/consumer code for common integrations
- Examples: Debezium (CDC from databases), S3 sink, JDBC source

## Schema Registry
- Centralized schema management (usually Avro, Protobuf, or JSON Schema)
- Ensures producers and consumers agree on message format
- Supports schema evolution (backward/forward compatibility)
- Prevents breaking changes from being published

## Common System Design Use Cases

| Use Case | How |
|---|---|
| **Event-driven architecture** | Decouple microservices via topics |
| **Log aggregation** | Collect logs from services → central pipeline |
| **Stream processing** | Real-time ETL, fraud detection, recommendations |
| **Change data capture (CDC)** | Database changes → Kafka via Debezium |
| **Activity tracking** | Clickstream, page views, user actions |
| **Metrics & monitoring** | Time-series data pipeline |
| **Event sourcing** | Compacted topics as source of truth for state |
| **Message queue replacement** | Consumer groups for work distribution |

## Kafka vs Redis Pub/Sub vs Traditional Message Queues

| Feature | Kafka | Redis Pub/Sub | RabbitMQ |
|---|---|---|---|
| **Durability** | Yes (disk-based) | No (fire-and-forget) | Yes (optional) |
| **Replay** | Yes (offset reset) | No | No (once consumed) |
| **Throughput** | Very high | Very high | Moderate |
| **Ordering** | Per-partition | No guarantee | Per-queue |
| **Consumer groups** | Yes (native) | No | Yes |
| **Latency** | Low ms | Sub-ms | Low ms |
| **Use case** | Event streaming, logs | Real-time notifications | Task queues, RPC |

## Key Limitations to Mention in Interviews
- **Not low-latency enough for real-time caching** – use Redis for sub-ms reads
- **Partition count is hard to change** – plan ahead; too few = bottleneck, too many = overhead
- **Ordering only per-partition** – need global ordering? Use single partition (kills parallelism)
- **Operational complexity** – cluster management, monitoring, tuning (broker configs, consumer lag, ISR health)
- **Not ideal for small messages with request-reply patterns** – better suited for async, high-volume streams
- **Consumer lag** – slow consumers can fall behind; need monitoring and alerting
- **Rebalancing storms** – adding/removing consumers triggers partition reassignment, can cause brief processing pauses

## Quick Numbers to Remember

| Metric | Value |
|---|---|
| Throughput | Millions of msgs/sec per cluster |
| Latency (produce → consume) | ~2–10ms typical |
| Default retention | 7 days |
| Typical replication factor | 3 |
| Max message size (default) | 1MB (configurable) |
| Partitions per topic | Tens to thousands |
| Typical cluster size | 3–30+ brokers |

## Key Configurations to Know

| Config | What It Controls |
|---|---|
| `replication.factor` | Number of copies per partition |
| `min.insync.replicas` | Min replicas for acks=all writes |
| `acks` | Producer durability guarantee |
| `retention.ms` / `retention.bytes` | How long/much data to keep |
| `num.partitions` | Default partitions for new topics |
| `max.message.bytes` | Max single message size |
| `enable.idempotence` | Exactly-once producer writes |

---

**Bottom line:** Reach for Kafka when you need durable, high-throughput event streaming, decoupled microservices, log aggregation, CDC, or replayable message pipelines. Avoid it for low-latency caching (use Redis), simple task queues (use SQS/RabbitMQ), or when operational complexity isn't justified by scale.
