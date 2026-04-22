# System Design Starting Skeletons by Communication Pattern

> **How to use:** Identify the communication pattern from the problem requirements, then start with the matching skeleton. Most real systems combine multiple patterns.

---

## Functional Requirements Checklist: ACTORS

Use this to make sure you cover all functional dimensions during clarification:

- **A** - Actions (what are the core operations? CRUD, increment, send, search?)
- **C** - Constraints (limits, deduplication, ordering, permissions, uniqueness?)
- **T** - Triggers (who/what initiates? end user, internal service, scheduled timer?)
- **O** - Output (what does the caller get back? response format, pagination?)
- **R** - Recovery (what happens on failure? retries, cancellation, editing?)
- **S** - State (can callers query status or history? what states exist?)

You don't need all 6 every time. A simple read-heavy system (URL shortener) might skip Recovery and State. A complex async system (task scheduler) hits all 6. Start with Actions and Constraints - those two shape the design the most.

**Target: 3-4 clarifying questions for a typical interview round, prioritize A, C, R.**
- **Actions** (1 question): "What are the core operations?" - this is mandatory, always ask.
- **Constraints** (1-2 questions): "Any ordering, dedup, rate limits, permissions?" - this shapes the design.
- **Recovery** (1 question): "What happens on failure? Do we need retries or idempotency?" - shows you think beyond the happy path.
- Skip T, O, S unless they're non-obvious. Triggers and Output are usually clear from context. State comes up naturally when you design the DB.

**Flow in interview:** "Here's what the system does (A), here are the rules (C), here's who calls it (T), here's what they get back (O), here's what happens when things break (R), and here's how they check on it (S)."

---

## NFR Checklist: SCALED

Use this to make sure you don't miss key non-functional requirements during clarification:

- **S** - Scalability (how many users, how much data, read-heavy or write-heavy?)
- **C** - Consistency (strong vs eventual? what data can't be stale?)
- **A** - Availability (can the system go down? what's the uptime target?)
- **L** - Latency (how fast do responses need to be?)
- **E** - Else (security, compliance, anything problem-specific)
- **D** - Durability / Fault Tolerance (can we lose data? what happens when things break?)

You don't ask about all of them every time. Pick the ones relevant to the problem. "Is this read-heavy or write-heavy?" is the single most impactful question - it drives half your architecture decisions.

**Target: 2-3 clarifying questions for a typical interview round, prioritize S and C.**
- **Scalability** (1 question, always ask): "How many users? Is this read-heavy or write-heavy?" - drives half your architecture.
- **Consistency** (1 question, usually ask): "Does this need strong consistency or is eventual OK?" - determines your DB/cache strategy. Remember: consistency = "do all users see the same thing right now?" (not "is the data safe" -- that's durability).
- **Latency** (1 question, if relevant): "What's the latency target?" - matters for real-time systems, less so for batch/async.
- Skip A, E, D unless the problem calls for them. Availability is almost always "yes, high availability" (not worth asking). Durability is almost always "yes, don't lose data." Else is for unusual requirements.

### Consistency vs Durability (Don't Confuse These)

- **Consistency** = How quickly do all users/replicas see the **latest** data? **OR** "Do all users see the same thing right now?"
- **Durability** = Is the data **safe** after a crash/failure?                 **OR** "Is the data still there after a crash?"

A system can be durable but inconsistent (data is safe on disk, but replicas are out of sync for a few seconds). And consistent but not durable (everyone sees the same value, but it's only in memory and a crash kills it).

**"What about accuracy?"** -- Accuracy isn't its own NFR. It maps to one of two questions:
- "Can we show stale data?" -- that's **Consistency (C)**. Eventual consistency = briefly inaccurate reads.
- "Can we show approximate data?" -- that's **Else (E)**. Things like HyperLogLog (~98% accurate) or approximate counters. You're choosing to sacrifice precision for performance.

### Strong vs Eventual Consistency: What It Means for Your Design

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

---

## API Design Checklist: ROPES

Use this when sketching out the API layer of your design:

- **R** - Resources (what are the entities/nouns? `/tasks`, `/users`, `/messages`)
- **O** - Operations (what HTTP verbs per resource? GET, POST, PUT, DELETE)
- **P** - Payloads (request body/query params, response shape, what fields?)
- **E** - Errors (status codes: 400 bad input, 404 not found, 429 rate limited, 500 server error)
- **S** - Specials (pagination, auth, rate limiting, versioning, idempotency keys)

You don't need to design a full API spec in the interview. State the resources, list 3-4 key endpoints with their verbs, and mention one or two specials that matter for the problem (e.g., "pagination on GET /messages" or "idempotency key on POST /payments").

**Example (Task Scheduler):**
```
POST   /tasks          - schedule a new task (body: callback_url, payload, scheduled_at)
GET    /tasks/{id}     - check task status (response: status, retry_count, scheduled_at)
DELETE /tasks/{id}     - cancel a pending task
GET    /tasks?service_id=X&status=failed  - list failed tasks for a service (paginated)
```

### API Design for Non-REST Protocols

ROPES is REST-focused, but most systems have a REST API for CRUD plus another protocol for real-time or async. Define both during the API phase.

**General principle:** The same core question applies regardless of protocol -- "what can clients do and how?" What changes is the format.

**WebSocket Events (Chat, Collaborative Editing, Multiplayer):**

No HTTP verbs. Define **event types** the client can send and the server can push.

```
Client -> Server:
  { type: "send_message",   payload: { chat_id, text } }
  { type: "typing_start",   payload: { chat_id } }
  { type: "typing_stop",    payload: { chat_id } }
  { type: "mark_read",      payload: { chat_id, message_id } }

Server -> Client:
  { type: "new_message",    payload: { message_id, sender_id, text, timestamp } }
  { type: "user_typing",    payload: { chat_id, user_id } }
  { type: "user_online",    payload: { user_id } }
  { type: "message_read",   payload: { chat_id, message_id, reader_id } }
```

Most chat/real-time systems need both REST and WebSocket APIs:
- **REST** for CRUD that doesn't need real-time: create account, fetch message history, update profile
- **WebSockets** for real-time events: send/receive messages, typing indicators, presence

**Kafka / Event-Driven (Service-to-Service):**

Define **topic names** and **event schemas**. These aren't client-facing -- they're how your internal services communicate.

```
Topic: chat.messages      -> { message_id, chat_id, sender_id, text, timestamp }
Topic: user.presence      -> { user_id, status, timestamp }
Topic: notifications.send -> { user_id, type, title, body, channel }
```

**gRPC (Service-to-Service):**

Define **service methods**. Rarely needed in interviews unless they ask about inter-service communication.

```
service ChatService {
  rpc SendMessage(SendRequest) returns (SendResponse);
  rpc StreamMessages(StreamRequest) returns (stream Message);
}
```

**Quick Decision: Which API(s) to Define**

| System type | Define during API phase |
|---|---|
| Standard CRUD (URL shortener, task scheduler) | REST only |
| Real-time + CRUD (chat, dashboard, collab editing) | REST + WebSocket events |
| Async processing (notification pipeline, analytics) | REST + Kafka topics |
| Full combo (chat with notifications) | REST + WebSocket events + Kafka topics |

---

## Database Design Checklist: TABLE

Use this when making storage decisions:

- **T** - Type (SQL vs NoSQL - driven by access pattern, not data volume)
- **A** - Anatomy (what entities/tables? what columns and data types?)
- **B** - Bindings (relationships: 1:1, 1:N, M:N, foreign keys, join tables; or denormalization for NoSQL)
- **L** - Lookups (what indexes? driven by your hot query paths)
- **E** - Expansion (partitioning, sharding, replication - how does it scale?)

Start with T (the SQL vs NoSQL decision drives everything else). State A and B together when you sketch the schema. L is where you show depth - connect each index to a specific query. E is your scaling story when the interviewer pushes.

**Target: Cover T, A, L. Keep B and E light.**
- **Type** (always, 1 sentence): State SQL or NoSQL and **why**. "Postgres because we need transactions for status updates." This is the most important decision -- get it right and justify it.
- **Anatomy** (always, sketch it): Name your tables and key columns. Don't list every field -- focus on the ones that matter for your queries and indexes.
- **Lookups** (this is where you show depth): Connect each index to a specific query path. "Compound index on `(status, scheduled_at)` because the poller queries by both." Tying indexes directly to query paths is a key depth signal.
- **Bindings** (keep light): Mention relationships if they exist ("users 1:N messages") but don't over-explain. If it's a single table, say so and move on.
- **Expansion** (mention when pushed): Don't bring up sharding/partitioning unprompted. When the interviewer asks "how does this scale?", that's when you talk about partitioning strategy and read replicas. Have an answer ready but don't volunteer it early.

### How to Think About Indexes

Your API design (step 4) tells you your hot queries. Your hot queries tell you your indexes. Indexes aren't a separate thing you invent -- they fall out of the API you already designed.

**The mental process:**

1. Look at your API endpoints (from step 4). Each endpoint = a query.
2. For each query, ask: "What columns am I filtering by in the WHERE clause or sorting by in ORDER BY?"
3. Those columns get an index.

**Example -- Task Scheduler:**

| API endpoint | Query it runs | Index needed |
|---|---|---|
| `GET /tasks/{id}` | `WHERE task_id = ?` | PK on `task_id` (automatic) |
| `GET /tasks?service_id=X&status=failed` | `WHERE service_id = ? AND status = ?` | Compound on `(service_id, status)` |
| Poller (internal) | `WHERE status = 'pending' AND scheduled_at <= NOW() ORDER BY scheduled_at` | Compound on `(status, scheduled_at)` |

**Example -- Chat System:**

| API endpoint | Query it runs | Index needed |
|---|---|---|
| `GET /chats/{id}/messages` | `WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 20` | Compound on `(chat_id, timestamp)` |
| `GET /users/{id}/chats` | `WHERE user_id = ? ORDER BY last_message_at DESC` | Compound on `(user_id, last_message_at)` |

**Compound index rule of thumb:** If a query filters on column A and sorts/filters on column B, make a compound index on `(A, B)`. Order matters -- put the equality filter first, range/sort second.

**Example (Task Scheduler):**
```
T - Postgres (need transactional status updates, atomic SELECT FOR UPDATE)
A - tasks table: task_id UUID PK, service_id, callback_url, payload JSONB,
    scheduled_at TIMESTAMP, status ENUM, retry_count INT, created_at, updated_at
B - Simple single table, no relationships needed (service_id is just a label, not a FK)
L - Compound index on (status, scheduled_at) for the poller hot path
    PK index on task_id for status lookups
E - Partition by scheduled_at (monthly) to keep active partitions small
    Read replicas for status query load if needed
```

---

## Interview Flow Summary

| Phase | Acronym | What you're doing |
|---|---|---|
| 1. Functional Reqs | **ACTORS** | What does the system do? |
| 2. Non-Functional Reqs | **SCALED** | How well does it need to do it? |
| 3. Capacity Estimation | **Traffic → Storage → Bandwidth → Memory** | How big is it? What does scale imply? |
| 4. API Design | **ROPES** | How do clients talk to it? |
| 5. Database Design | **TABLE** | How is data stored and queried? |
| 6. High-Level Architecture | *(skeletons below)* | How do the boxes connect? |
| 7. Deep Dive | *(interviewer picks)* | Prove depth on one area |

---

## Back-of-Envelope Calculations

> **When to do this:** After SCALED (NFRs), before drawing architecture. Takes 3-5 minutes. Interviewers want to see you can reason about scale, not that you memorize exact numbers.

### The 4 Dimensions

Everything derives from **traffic**. Estimate traffic first, then multiply through:

```
Traffic (QPS)
  ├── × payload size     = Bandwidth
  ├── × record size × retention = Storage
  └── × cache ratio      = Memory
```

| Dimension | What you're estimating | Formula | Units |
|---|---|---|---|
| **Traffic** | How many requests/sec? | DAU × actions/user/day ÷ 86,400 | QPS |
| **Storage** | How much disk over time? | QPS × record size × seconds in retention period | GB/TB |
| **Bandwidth** | How much network I/O? | QPS × avg payload size | MB/s |
| **Memory** | How much RAM for caching? | Cache the hot subset (80/20 rule or explicit %) | GB |

### Step-by-Step Flow

**Step 1: Traffic (always start here)**
```
Given: 10M DAU, each user sends 20 messages/day

Write QPS = 10M × 20 / 86,400 ≈ 2,300 QPS
Peak QPS  = 2,300 × 2 (or ×3) ≈ 5,000 QPS (assume 2-3x peak factor)

Read:Write ratio? Chat is ~10:1 reads per write
Read QPS  = 2,300 × 10 ≈ 23,000 QPS
```
**Shortcut:** 86,400 seconds/day ≈ ~100K. So "X per day" ÷ 100K ≈ QPS. (Slightly overestimates, which is fine for estimation.)

**Step 2: Storage**
```
Per message: sender_id (8B) + receiver_id (8B) + text (500B avg) + metadata (100B) ≈ 600B

Daily:  2,300 QPS × 86,400 sec × 600B ≈ 120 GB/day
Yearly: 120 GB × 365 ≈ 43 TB/year

With replication (×3): ~130 TB/year
```

**Step 3: Bandwidth**
```
Incoming (writes): 2,300 QPS × 600B ≈ 1.4 MB/s
Outgoing (reads):  23,000 QPS × 600B ≈ 14 MB/s

Not a bottleneck here. Bandwidth matters more when payloads are large (images, videos).
```

**Step 4: Memory (Cache)**
```
80/20 rule: 20% of data serves 80% of reads

Daily data: 120 GB
Cache 20%:  120 GB × 0.20 = 24 GB  (fits in a single Redis instance)

Or: cache the last N hours of messages
Last 1 hour: 2,300 × 3,600 × 600B ≈ 5 GB
```

### Numbers You Should Know

**Latency (order of magnitude):**

| Operation | Latency |
|---|---|
| L1 cache | ~1 ns |
| RAM access | ~100 ns |
| SSD read | ~100 us |
| Network round-trip (same DC) | ~500 us |
| HDD seek | ~10 ms |
| Network round-trip (cross-continent) | ~150 ms |

**Scale shortcuts:**

| Shortcut | Value |
|---|---|
| Seconds in a day | ~86,400 ≈ ~100K |
| Seconds in a month | ~2.5M |
| Seconds in a year | ~31.5M ≈ ~30M |
| 1 million bytes | ~1 MB |
| 1 billion bytes | ~1 GB |
| 1 trillion bytes | ~1 TB |

**Capacity rules of thumb:**

| Resource | Rough capacity |
|---|---|
| Single Redis instance | ~25-100 GB RAM, ~100K QPS |
| Single Postgres | ~1-5 TB, ~10K QPS (depends on query complexity) |
| Single Kafka broker | ~50-100K messages/sec |
| Single web server | ~1-10K QPS (depends on work per request) |

### When Each Dimension Actually Matters

Not every problem needs all 4. Focus on the ones that drive architecture decisions:

| Dimension | When it drives decisions | Example |
|---|---|---|
| **Traffic** | Always - determines how many servers, whether you need sharding | "50K QPS means we need multiple DB shards" |
| **Storage** | When data grows unbounded or retention is long | "43 TB/year means we need partitioning strategy" |
| **Bandwidth** | When payloads are large (media, files) | "Users upload 5MB images at 1K QPS = 5 GB/s incoming" |
| **Memory** | When you need to justify cache sizing or in-memory stores | "24 GB hot set fits in one Redis box" |

### Target: 0 questions, 2-3 minutes, state assumptions.

You're not asking the interviewer anything here. You state assumptions and let them correct you. Focus on Traffic and Storage -- those two drive architecture decisions. Only do Bandwidth and Memory if they're clearly relevant (large payloads, or you need to justify cache sizing).

### Interview Tips

- **Round aggressively.** 86,400 ≈ 100K. Nobody expects precision.
- **State assumptions out loud.** "I'll assume 10M DAU with 20 messages per user per day" - let the interviewer correct you.
- **Connect estimates to decisions.** Don't just calculate - say what it means: "23K read QPS means we need caching" or "43 TB/year means we need a partitioning strategy."
- **Peak vs average.** Multiply average by 2-3x for peak. If you're designing for peak, say so.
- **Don't spend more than 3-5 minutes.** This is a means to an end (justifying architecture choices), not the goal itself.

### Quick Template (Copy This)

```
Assumptions:
- DAU: ___
- Actions per user per day: ___
- Avg payload/record size: ___

Traffic:
- Write QPS: ___ DAU × ___ actions / 100K ≈ ___ QPS
- Read:Write ratio: ___:1
- Read QPS: ___ × ___ ≈ ___ QPS
- Peak: ×2-3 → ___ QPS

Storage:
- Per record: ___ bytes
- Daily: ___ QPS × 86,400 × ___ bytes ≈ ___ GB/day
- Yearly: ___ × 365 ≈ ___ TB/year
- With replication (×3): ___

Bandwidth:
- In:  ___ write QPS × ___ bytes ≈ ___ MB/s
- Out: ___ read QPS × ___ bytes ≈ ___ MB/s

Memory (Cache):
- 80/20 rule: daily ___ GB × 0.2 ≈ ___ GB
- Or cache last ___ hours: ___

→ Architecture implication: ___
```

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

### Which problems use which skeleton

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

**HyperLogLog:** Probabilistic data structure that estimates unique counts using ~12KB of memory regardless of set size (~98% accurate). Use when the interviewer says "unique" or "distinct" at scale (unique visitors, distinct users). Regular counters are for total counts. Redis has it built in: `PFADD key element`, `PFCOUNT key`.

**Most real systems are a combination.** A chat app is WebSockets for messages + REST for user profiles + Kafka for message persistence. Your job is to identify which parts of the system need which protocol.

---

## SSE vs Long Polling vs WebSockets

SSE and long polling both solve "server pushes to client" but are different mechanisms.

**Long Polling (hack/workaround):**
```
Client: "Anything new?"  -> Server holds request open...
                            ...waits...
                            ...data arrives -> responds
Client: "Anything new?"  -> Server holds again...  (repeat forever)
```
Each cycle = full HTTP request/response overhead. It's a workaround, not a real protocol.

**SSE (actual protocol for server push):**
```
Client: GET /events  ->  Server holds connection open indefinitely
                         <- data: new email arrived
                         <- data: notification update
                         <- data: dashboard metric
                         (connection stays open, server keeps pushing)
```
One long-lived HTTP connection. Built-in browser API (`EventSource`), auto-reconnection, and event IDs.

### Comparison Table

| | Long Polling | SSE | WebSockets |
|---|---|---|---|
| Connection | Repeated open/close | Single persistent HTTP | Single persistent TCP |
| Direction | Server -> Client (simulated) | Server -> Client (native) | Bidirectional |
| Overhead | High (new request each time) | Low | Lowest |
| Browser support | Everything | Everything modern | Everything modern |
| Use case | Fallback/legacy | Notifications, feeds, dashboards | Chat, games, collaboration |

**Rule of thumb:** SSE replaced long polling. Long polling is the fallback you mention for environments where SSE/WebSockets aren't supported (old proxies, corporate firewalls). You'd almost never design a new system around long polling by choice.

---

## Kafka vs Traditional Message Queues (SQS, RabbitMQ)

Kafka is not a traditional message queue - it's a distributed append-only log.

**Traditional Queue (SQS, RabbitMQ):**
```
Producer -> Queue -> Consumer picks up message -> MESSAGE DELETED
```
- Message **removed** after consumption
- Each message delivered to **one consumer**
- Like a to-do list: grab a task, complete it, it's gone

**Kafka (Distributed Log):**
```
Producer -> Topic (append-only log) -> Consumer A reads at offset 5
                                    -> Consumer B reads at offset 3
                                    -> Consumer C reads at offset 5
                                    (messages stay in the log)
```
- Messages **never deleted** after consumption (retained for configured period)
- Consumers track their position (offset) independently
- **Multiple consumer groups** read the same topic at their own pace
- Any consumer can **rewind** and reprocess old messages

### When to Reach for Which

**Use SQS/RabbitMQ when:**
- You have a task that needs to happen once and you don't care about it after: "send this email," "resize this image," "process this payment"
- One producer, one consumer (or competing consumers doing the same job)
- You want simplicity - less infrastructure to manage

**Use Kafka when:**
- Multiple services need to react to the same event: "user signed up" triggers welcome email AND analytics AND recommendations (three consumer groups, one topic)
- You need high throughput (millions of events/sec) - Kafka is built for this, SQS has per-message overhead
- You might need to reprocess data - consumer had a bug? Rewind the offset and replay. With SQS, messages are gone after consumption.
- You need ordering guarantees - Kafka preserves order within a partition

**Simple decision:** If you're just handing off a task to a worker, use SQS/RabbitMQ. If multiple systems need to independently consume the same stream of events, use Kafka.

**Note:** Clients never publish directly to a queue. There's always a service in between for validation, authentication, and protocol translation. The pattern is always: `Client --HTTP/WS--> API Service --> Queue`

---

## Kafka vs Redis Pub/Sub (Don't Confuse These)

Kafka is sometimes called a "pub/sub system" because multiple consumers can read the same topic. This is misleading - they work very differently.

**Redis Pub/Sub** - Like shouting in a room. If you're listening, you hear it. If not, it's gone.
```
Publisher -> "hey" -> Subscriber A gets it instantly
                   -> Subscriber B gets it instantly
                   -> message is gone forever
```
- Fire-and-forget, no persistence
- Sub-millisecond latency
- If nobody is subscribed, message disappears

**Kafka** - Like writing in a notebook that multiple people can read at their own pace.
```
Producer -> "hey" -> written to log at offset 7

Consumer Group A reads offset 7 (whenever it's ready)
Consumer Group B reads offset 7 (whenever it's ready)
Consumer Group C reads offset 7 (three weeks later, still there)
```
- Persistent log, messages retained for configured period
- Higher latency than Redis Pub/Sub
- Consumers can rewind and reread

**When you need both (e.g., chat system):**
- Redis Pub/Sub for instant delivery to connected users (speed matters, loss is OK because Kafka has the durable copy)
- Kafka for persistence, offline delivery, and async work (durability matters, latency is fine)

**Interview phrasing:** "I'd use Redis Pub/Sub for real-time delivery since it's fire-and-forget with sub-millisecond latency, and Kafka for durable persistence since messages are retained and can be replayed."

---

## SQL vs NoSQL Decision Framework

### How to Spot It From the Problem

Ask yourself: "Does anyone need to ask questions about the data beyond simple lookups?"

- **Simple lookup** = "give me this one thing by its ID" or "give me all things for this user" --> NoSQL is fine
- **Complex query** = "give me the count/sum/average of things, grouped by some dimension, filtered by multiple conditions" --> you need SQL

**Signals from ACTORS that point to SQL:**

| ACTORS signal | Why it needs SQL |
|---|---|
| "Show analytics/reports/dashboards" | Aggregations (COUNT, SUM, AVG, GROUP BY) |
| "Search/filter by multiple fields" | Multi-column WHERE clauses |
| "Leaderboard / ranking" | ORDER BY + LIMIT across all data |
| "Billing / invoices" | JOINs across users, orders, line items + transactions |
| "Admin panel to manage X" | Ad-hoc queries on many columns, filtering, sorting |
| "Detect duplicates / conflicts" | Unique constraints, transactional checks |

**Signals that say NoSQL is fine:**

| ACTORS signal | Why NoSQL works |
|---|---|
| "Get user profile by ID" | Single key lookup |
| "Get messages for this chat" | Partition key lookup (chat_id) |
| "Store session data" | Key-value, no relationships |
| "High write volume, simple reads" | Built-in sharding, no JOINs needed |

**One-liner:** If your API endpoints only ever query by one or two known keys, NoSQL works. The moment someone needs to slice the data in flexible/unexpected ways, reach for SQL.

### The Decision Tree

```
Do I need JOINs or transactions?
  YES -> SQL
  NO  -> Are access patterns simple key-value lookups?
           YES -> NoSQL
           NO  -> Probably SQL (complex queries are easier in SQL)
```

**Choose SQL (Postgres/MySQL) when:**
- Data has relationships (users have orders, orders have items - you need JOINs)
- You need transactions (debit one account AND credit another, both or neither)
- You need complex queries (GROUP BY, aggregations, filtering on multiple columns)

**Choose NoSQL (DynamoDB/Cassandra) when:**
- Simple access patterns (get by key, put by key)
- Write-heavy at scale (built-in sharding)
- Data doesn't have complex relationships

**Scaling difference:**
- SQL: you manage sharding yourself (complex)
- NoSQL: sharding is built in (you just pick the partition key)

**Interview tip:** If you pick DynamoDB or Cassandra, either is fine. DynamoDB is simpler to explain (managed service, zero ops). Cassandra gives you more control and is multi-cloud portable. Pick one and stick with it.
