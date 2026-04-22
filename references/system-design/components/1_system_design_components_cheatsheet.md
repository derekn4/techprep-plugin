# System Design Components Cheat Sheet

A comprehensive reference of building blocks expected in a typical system design interview.

---

## Clients & Entry Points
- **Mobile/Web clients** – the end-user interface
- **DNS** (Route 53) – domain name resolution, latency-based or geo routing
- **CDN** (CloudFront, Akamai) – edge caching for static assets (images, JS, CSS, video), reduces latency for global users

## API & Routing Layer
- **API Gateway** – single entry point for clients. Handles rate limiting, authentication, request routing, SSL termination, request/response transformation
- **Load Balancers** – distribute traffic across servers
  - L4 (transport layer) – routes based on IP/port, faster
  - L7 (application layer) – routes based on HTTP headers/URL/cookies, smarter
  - Algorithms: round-robin, least connections, weighted, consistent hashing
- **Reverse Proxy** (Nginx, HAProxy) – sits in front of servers, handles SSL, compression, caching

## Compute
- **Application servers** – stateless, horizontally scalable. Store no local state (put it in cache/DB).
- **Microservices vs Monolith** – microservices for independent scaling/deployment; monolith for simplicity early on
- **Serverless** (Lambda) – event-driven, auto-scaling, pay-per-invocation. Good for async tasks, webhooks, lightweight APIs.

## Caching
- **Cache layers:** client-side → CDN → API gateway → application (Redis/Memcached) → database query cache
- **Strategies:**
  - **Cache-aside** – app checks cache first, loads from DB on miss, writes to cache
  - **Write-through** – Write to DB first, then cache near simultaneous (consistent, slower writes) 
  - **Write-behind (write-back)** – write to cache, async flush to DB (fast writes, risk of data loss)
  - **Read-through** – cache itself loads from DB on miss
- **Eviction:** LRU, LFU, TTL-based
- **Invalidation** – the hard problem. TTL expiry, event-driven invalidation, or versioned keys
- **Tools:** Redis (feature-rich, data structures), Memcached (simpler, multi-threaded, pure cache)

## Databases

### SQL (Relational)
- PostgreSQL, MySQL
- ACID transactions, strong consistency, joins, complex queries
- Best for: structured data, relationships, financial data, transactional workloads
- Scaling: read replicas, vertical scaling, sharding (harder)

### NoSQL
| Type | Examples | Best For |
|---|---|---|
| **Key-Value** | Redis, DynamoDB | Caching, sessions, simple lookups |
| **Wide-Column** | Cassandra, HBase | Time-series, IoT, write-heavy |
| **Document** | MongoDB, CouchDB | Flexible schemas, catalogs, content |
| **Graph** | Neo4j, Neptune | Social networks, recommendations |

### Database Concepts to Know
- **Sharding** – horizontal partitioning across nodes
  - Hash-based (even distribution) vs range-based (good for range queries)
  - Hot spots and rebalancing challenges
- **Replication** – leader-follower (read scaling), leaderless (availability), multi-leader (multi-region)
- **Indexing** – B-tree (reads), LSM tree (writes), composite indexes
- **Read replicas** – offload read traffic from primary
- **Denormalization** – duplicate data to avoid joins (trade storage for speed)
- **Connection pooling** – reuse DB connections to avoid overhead

## Message Queues & Event Streaming

### Message Queues (Task Processing)
- **SQS, RabbitMQ** – point-to-point, task distribution
- Messages consumed once, deleted after processing
- Dead letter queues (DLQ) for failed messages
- Good for: async job processing, decoupling services

### Event Streaming
- **Kafka** – high-throughput, durable, replayable event log
- Messages retained regardless of consumption
- Consumer groups for parallel processing
- Good for: event-driven architecture, CDC, log aggregation, real-time pipelines

### Key Concepts
- At-most-once, at-least-once, exactly-once delivery
- Backpressure handling
- Ordering guarantees (per-partition in Kafka, FIFO in SQS FIFO)

## Search
- **Elasticsearch** – distributed full-text search engine built on inverted indexes
- Supports: fuzzy matching, autocomplete, faceted search, relevance scoring
- Often paired with Kafka for real-time indexing
- Use case: search bars, log search (ELK stack), product search

## Blob / Object Storage
- **S3** (or GCS, Azure Blob) – store images, videos, files, backups
- Paired with CDN for fast global delivery
- Lifecycle policies for archival (S3 → Glacier)
- Pre-signed URLs for secure direct uploads/downloads

## Notification & Real-Time Communication

| Method | Direction | Use Case |
|---|---|---|
| **WebSockets** | Bidirectional | Chat, live collaboration, gaming |
| **SSE (Server-Sent Events)** | Server → Client | Live feeds, notifications, dashboards |
| **Long Polling** | Client → Server (held) | Fallback when WebSockets unavailable |
| **Push Notifications** | Server → Device | Mobile alerts (APNs, FCM) |

## Rate Limiting & Throttling
- **Algorithms:**
  - **Token bucket** – tokens refill at fixed rate, each request costs a token (most common)
  - **Sliding window** – count requests in a rolling time window
  - **Leaky bucket** – requests processed at fixed rate, excess queued/dropped
  - **Fixed window** – simple but has boundary burst problem
- Usually at API gateway or dedicated service backed by Redis (INCR + EXPIRE)
- Rate limit by: user ID, IP, API key, endpoint

## Consistent Hashing
- Distributes data/load across nodes in a ring
- Adding/removing nodes only remaps a fraction of keys (vs rehashing everything)
- **Virtual nodes** – each physical node maps to multiple points on the ring for better balance
- Used in: cache distribution, DB sharding, Kafka partitioning, CDNs

## Data Processing

### Batch Processing
- Process large datasets on a schedule (hourly, daily)
- Tools: MapReduce, Spark, Hadoop
- Use case: analytics, reports, ML training

### Stream Processing
- Process data in real-time as it arrives
- Tools: Kafka Streams, Flink, Spark Streaming
- Use case: fraud detection, real-time recommendations, live dashboards

### ETL Pipelines
- Extract → Transform → Load
- Move and reshape data between systems (operational DB → data warehouse)

## Monitoring & Observability
- **Logging** – structured logs, centralized (ELK stack: Elasticsearch + Logstash + Kibana)
- **Metrics** – system/application metrics (Prometheus + Grafana)
- **Distributed Tracing** – trace requests across microservices (Jaeger, Zipkin)
- **Alerting** – PagerDuty, CloudWatch alarms
- Mention briefly in interviews to show production awareness

## Unique ID Generation

| Approach | Pros | Cons |
|---|---|---|
| **Auto-increment** | Simple, sortable | Single point of failure, doesn't scale |
| **UUID** | No coordination needed | 128-bit, not sortable, storage heavy |
| **Snowflake ID** | Sortable, distributed, 64-bit | Clock skew issues, machine ID management |
| **DB ticket server** | Simple, sortable | SPOF unless replicated |
| **ULID** | Sortable UUID alternative | Less common |

Snowflake structure: `timestamp (41 bits) + machine ID (10 bits) + sequence (12 bits)`

---

## Key Concepts to Weave Into Any Design

### CAP Theorem
- **Consistency** – every read returns the latest write
- **Availability** – every request gets a response
- **Partition Tolerance** – system works despite network partitions
- In practice, partitions happen, so you choose CP or AP

### Consistency Models
- **Strong** – linearizable, read-after-write guaranteed
- **Eventual** – replicas converge over time
- **Causal** – preserves cause-and-effect ordering

### Scaling
- **Vertical** – bigger machine (simpler, has limits)
- **Horizontal** – more machines (complex, scales further)
- Stateless services → easy horizontal scaling
- Stateful services → need sharding, replication, or sticky sessions

### Estimation (Back-of-the-Envelope)
- QPS (queries per second) – DAU × actions/user ÷ 86,400
- Storage – items × item size × retention period
- Bandwidth – QPS × average response size
- Know your powers of 2 and rough latency numbers

### Reliability
- Eliminate single points of failure (redundancy at every layer)
- Idempotency for safe retries
- Circuit breakers to prevent cascade failures
- Graceful degradation (serve stale cache, disable non-critical features)
- Health checks and auto-recovery

---

**How to use this in an interview:** Start with requirements → estimate scale → draw the high-level architecture using these components → deep dive into the most critical parts → discuss tradeoffs and failure scenarios.
