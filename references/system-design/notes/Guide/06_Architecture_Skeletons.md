# Step 6: High-Level Architecture - Skeletons

> **Goal:** Draw the boxes and arrows. Pick the right communication pattern, then customize. ~15 minutes.

---

## How to Use This

1. Identify the communication pattern from your requirements (use the quick reference at the bottom)
2. Start with the matching skeleton
3. Customize: add/remove components based on your specific problem
4. Most real systems combine multiple patterns

---

## REST (Request-Response)

```
Client -> LB -> API Gateway -> Services -> Cache -> DB
```

**Use when:** Standard CRUD, client asks and server responds

**GraphQL variant:** Same skeleton, but replace the API Gateway/Services layer with a GraphQL server that lets clients specify exactly what data they want in one request. Reach for GraphQL over REST when multiple client types (mobile, web, third-party) need different shapes of the same data, or when clients would otherwise need multiple round-trips to fetch nested/related resources. If it's simple CRUD with one client type, REST is simpler and sufficient.

```
GraphQL: Client -> LB -> API Gateway -> GraphQL Server -> Cache -> DB
                              |
                              └-> Other Services (auth, notifications, file uploads)
```

---

## WebSockets (Bidirectional Real-Time)

```
Client <--WS connection--> LB (sticky sessions) -> WS Servers
                                                      |
                                                  Pub/Sub (Redis)
                                                      |
                                                  WS Servers (other instances)

Write path: Client -> WS Server -> Queue (Kafka) -> Workers -> DB
Read path:  DB/Cache -> WS Server -> push to Client
```

**Use when:** Both sides need to push data - chat, collaborative editing, multiplayer games

**Key differences from REST:**
- Connections are persistent and stateful
- LB needs **sticky sessions** (user stays on same server)
- Need a **pub/sub layer** for cross-server fanout (User A on Server 1 sends message to User B on Server 2)
- Need a **connection registry** (which user is on which server)

---

## SSE - Server-Sent Events (Server Push Only)

```
Client --HTTP GET--> LB -> API Server (holds connection open)
                              |
                          Pub/Sub (Redis) <-- Event producers (other services/workers)

Writes still go through normal REST:
Client --POST--> LB -> API Gateway -> Services -> DB
```

**Use when:** Only the server needs to push - live dashboards, notifications, activity feeds, score updates

**Key difference from WebSockets:** Simpler. Long-lived HTTP response that keeps streaming. No special LB config needed. Client can't send data back over the same connection (uses regular REST for that).

---

## Event-Driven / Message Queue (Async Processing)

```
Producer (API/Service) -> Message Queue (Kafka/SQS) -> Consumer Workers -> DB/Cache
                              |
                          Dead Letter Queue (failed messages)
```

**Use when:** Work doesn't need an immediate response - email sending, image processing, analytics ingestion, notifications

**Not a client-facing protocol** - it's for service-to-service communication. Almost always combined with one of the above:

```
Client --REST--> API -> DB (ack to client)
                   |
                   -> Kafka -> Email Worker -> Email Provider
                            -> Analytics Worker -> Data Warehouse
                            -> Notification Worker -> Push Service
```

---

## Poller Pattern (Scheduled / Delayed Processing)

```
                    ┌─────────────────────────────┐
                    │         Poll loop            │
                    │  sleep(N) -> query -> batch  │
                    └─────────────────────────────┘
                                 |
API -> DB (write)     Poller(s) -> DB (SELECT ... FOR UPDATE SKIP LOCKED)
                                 |
                          Queue (Kafka) -> Workers -> [execute / call external service]
                                 |
                          Update DB status (completed/failed)
```

**Use when:** Work needs to happen later, not immediately. The "when to process" decision lives in the data, not in the event stream.

**How it works:**
1. API writes a record to the DB with a future timestamp or pending status
2. One or more pollers run in a loop: sleep, query for due items, grab a batch
3. Pollers push work to a queue (or process directly for simple cases)
4. Workers execute and update status

**Key design decisions:**
- **Poll interval** - balance between precision and DB load (typically 1-10 seconds)
- **Batch size** - grab 50-500 items per poll cycle, not one at a time
- **Multiple pollers** - use `SELECT ... FOR UPDATE SKIP LOCKED` so they divide work without coordination
- **What to do with items** - push to Kafka (decouple, absorb bursts) or process directly (simpler, fewer components)

**Preventing double-pickup (the critical pattern):**
```sql
BEGIN;
SELECT * FROM {table}
WHERE {condition}       -- e.g. status = 'pending' AND due_at <= NOW()
ORDER BY {priority}     -- e.g. due_at ASC, created_at ASC
LIMIT {batch_size}      -- e.g. 100
FOR UPDATE SKIP LOCKED;

-- mark as claimed, then push to queue or process
UPDATE {table} SET status = 'processing' WHERE id IN (...);
COMMIT;
```
Multiple pollers run this concurrently. `SKIP LOCKED` means each one grabs different rows. No coordination layer needed.

**Crash safety:**
- Poller crashes before commit -> Postgres rolls back, rows stay in original state, other pollers pick up
- Worker crashes mid-execution -> stale item **reaper** (itself a poller!) resets stuck items after a timeout

**Where you'll see this pattern:**

| System | What's being polled | Trigger condition |
|---|---|---|
| Task scheduler | Scheduled tasks | `scheduled_at <= now()` |
| Stale task reaper | Stuck tasks | `status = 'running' AND updated_at < now() - 5min` |
| Outbox pattern | Unsent events | `published = false` |
| Delayed retries | Failed jobs | `retry_after <= now()` |
| Subscription billing | Due invoices | `next_billing_date <= today()` |
| Data cleanup / TTL | Expired records | `expires_at <= now()` |

**Poller vs Event-Driven - when to use which:**

| | Poller | Event-Driven (Queue) |
|---|---|---|
| Trigger | Time-based or condition-based (poll the DB) | Event-based (something just happened) |
| Latency | Seconds (depends on poll interval) | Near-instant |
| Complexity | Simple (just a loop + SQL query) | More infrastructure (Kafka/SQS setup) |
| Best for | "Do X at time Y" / "clean up stale things" | "When X happens, do Y" |

**They often work together:** API writes to DB, poller finds due items and pushes to Kafka, workers drain Kafka. The poller bridges "delayed trigger" with "async execution."

---

## gRPC (Service-to-Service)

```
Client --REST/WS--> API Gateway -> Service A --gRPC--> Service B
                                             --gRPC--> Service C
```

**Use when:** Internal microservice communication needing low latency, strong typing, or streaming between services

Rarely needs to be drawn out in interviews unless they specifically ask about inter-service communication. Mention: "Services communicate via gRPC internally for lower latency and schema enforcement via Protocol Buffers."

---

## Backend System Design: Common Skeleton

Most backend system design problems (6 out of 10 common ones) start from this same skeleton:

```
Client -> LB -> API Gateway -> Service -----> Cache (Redis) -> DB
                                  |                ▲              ▲
                                  └-> Queue -> Workers ──────────┘
```

- **Read path:** Service -> Cache -> DB (on miss)
- **Write path:** Service -> Queue -> Workers -> DB + Cache

Not every problem uses every piece. Remove what you don't need rather than adding what you didn't plan for.

### Which Problems Use Which Skeleton

| Problem | Skeleton | What's different |
|---|---|---|
| Distributed counter | Common | Workers batch-sum before writing |
| Notification delivery | Common | Workers call external providers (email/push/SMS) |
| Rate limiter | Common (simplified) | Mostly just Service + Redis, minimal queue usage |
| Analytics pipeline | Common | Workers aggregate, write to data warehouse instead of regular DB |
| Job/task queue | Common | You're designing the queue + workers layer itself |
| Task scheduler | Poller + Event-Driven | API -> DB, poller queries for due tasks, pushes to Kafka, workers fire webhooks |
| Subscription billing | Poller | Poller queries for due invoices, generates charges |
| Stale item reaper | Poller | Poller finds stuck/expired items, resets or cleans up |
| Outbox pattern | Poller + Event-Driven | Poller finds unpublished events in DB, pushes to Kafka for downstream consumers |
| URL shortener | Common (simplified) | Read-heavy, cache is the star, queue barely needed |
| Autocomplete | Specialized read | Trie/cache as read path, offline rebuild pipeline |
| Email search | Specialized read | Elasticsearch as read path, indexing pipeline |
| Real-time sync | Common + WebSockets | Adds WS servers + pub/sub for pushing updates |
| Distributed cache | Special | You're designing the cache layer itself (consistent hashing, replication, eviction) |

### Exception: Specialized Read Path (Autocomplete / Search)

```
Client -> LB -> API Gateway -> Service -> Trie Cache (Redis) ──or── Elasticsearch
                                               ▲
                                               │ rebuild/re-index
                                               │
                                  Queue -> Workers (aggregate data, build index)
                                    ▲
                                    │
                              Data sources (query logs, emails, etc.)
```

The read path goes to a **specialized data structure** (Trie or inverted index) instead of a general DB. The write path is an **offline pipeline** that rebuilds that structure periodically, not real-time writes.

### Exception: Real-Time Sync (Common + WebSockets)

```
Client <--WS--> LB (sticky) -> WS Servers
                                    |
                                Pub/Sub (Redis)
                                    |
                                WS Servers (other instances)

Write path: Client -> API Service -> DB -> Queue -> Workers -> Pub/Sub -> WS Servers -> push to clients
Read path:  Client -> API Service -> Cache -> DB
```

After a write is processed, the system **pushes the update back out** to connected clients through pub/sub. The common skeleton only stores data - this one also delivers it in real-time.

---

## Common Skeleton Combinations

Real systems combine multiple skeletons. Here are the patterns you'll see most often:

### Combo 1: REST + Queue (most common)
```
Client -> API -> DB (ack to client)
                  |
                  └-> Queue -> Workers -> [external service / DB / cache]
```
**Examples:** Notification system, image processing, email sending, payment processing
**When:** Client needs a fast response, but there's background work to do

### Combo 2: REST + Queue + Specialized Read Store
```
Write: Client -> API -> Queue -> Workers -> build/update index
Read:  Client -> API -> Trie / Elasticsearch / Data Warehouse
```
**Examples:** Autocomplete, email search, analytics dashboard
**When:** Read path needs a different data structure than what you write to

### Combo 3: REST + WebSockets
```
REST:  Client --HTTP--> API -> DB (CRUD operations)
WS:    Client <--WS---> WS Servers <-> Pub/Sub (real-time updates)
```
**Examples:** Real-time sync, collaborative editing, live dashboard with user actions
**When:** You need both standard CRUD and real-time push

### Combo 4: REST + Queue + WebSockets (the full combo)
```
Client --HTTP--> API -> DB -> Queue -> Workers -> Pub/Sub -> WS Servers -> push to clients
Client <--WS--> WS Servers
```
**Examples:** Chat system, notification system with live delivery, real-time collaborative tools
**When:** Writes are async, AND clients need real-time updates about those writes

### Combo 5: REST + SSE
```
Write: Client --POST--> API -> DB -> Queue -> Workers
Read:  Client --GET/SSE--> API -> stream updates as they happen
```
**Examples:** Live activity feed, order tracking, build/deploy status
**When:** Server pushes updates but client doesn't need to send data back in real-time

### Common Bolt-Ons (add to any skeleton based on NFRs)

| NFR signal | Bolt on |
|---|---|
| "Global users" | CDN for static content, multi-region deployment |
| "Users need to search" | Elasticsearch alongside primary DB |
| "Analytics / reporting" | Separate queue -> data warehouse (don't query production DB) |
| "Abuse prevention" | Rate limiter at API Gateway (Redis counters) |
| "File/image uploads" | S3 + CDN, separate upload endpoint |
| "Mobile users" | Push notification service (APNs/FCM) via queue |

---

## Quick Reference: Which Template to Start With

| Signal from interviewer | Start with |
|---|---|
| "Standard API" / "CRUD operations" | REST |
| "Multiple client types need different data" / "flexible queries" | REST with GraphQL |
| "Users need to see updates instantly" / "real-time" | WebSockets (if bidirectional) or SSE (if server-push only) |
| "Chat" / "collaborative" / "multiplayer" | WebSockets |
| "Live dashboard" / "notifications" | SSE + REST for writes |
| "Process X in the background" / "don't block the user" | REST + Message Queue |
| "High write throughput" / "millions of events" | REST + Message Queue + Batch workers |
| "Count unique/distinct X at scale" | Common skeleton + HyperLogLog |

**Most real systems are a combination.** A chat app is WebSockets for messages + REST for user profiles + Kafka for message persistence. Your job is to identify which parts of the system need which protocol.
