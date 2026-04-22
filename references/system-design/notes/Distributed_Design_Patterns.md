# Distributed System Design Patterns

> Reusable templates for building scalable, reliable, and maintainable systems. You're already using many of these without naming them.

---

## 1. CQRS (Command Query Responsibility Segregation)

**What it is:** Use separate models (and often separate databases) for reads and writes.

**Why:** Reads and writes have very different requirements. Writes need consistency and validation. Reads need speed and can tolerate staleness. Separating them lets you optimize each independently.

```
                    ┌──────────────────┐         ┌──────────────┐
  POST/PUT/DELETE   │  Write Service   │────────►│  Write DB    │
  ─────────────────►│  (commands)      │         │  (normalized)│
                    └──────────────────┘         └──────┬───────┘
                                                        │ sync (event/CDC)
                    ┌──────────────────┐         ┌──────▼───────┐
  GET               │  Read Service    │────────►│  Read DB     │
  ─────────────────►│  (queries)       │         │  (denormalized,│
                    └──────────────────┘         │   optimized)  │
                                                 └──────────────┘
```

**Example designs where this shows up:**
- **Distributed Counter** - writes go through Kafka pipeline to Cassandra, reads go to Redis. Different paths, different stores.
- **E-commerce product catalog** - writes go to normalized SQL DB, reads served from denormalized search index (Elasticsearch).
- **Social media feed** - writes update the posts table, reads served from a pre-computed feed cache.

---

## 2. Two-Phase Commit (2PC)

**What it is:** A protocol to make multiple databases/services commit or rollback together. All or nothing.

**Why:** When a single operation touches multiple databases (e.g., transfer money between two banks), you need them to either both succeed or both fail.

```
                         ┌──────────────┐
                         │ Coordinator  │
                         └──────┬───────┘
                    Phase 1:    │    "Can you commit?"
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │ Service A│ │ Service B│ │ Service C│
             │  "Yes"   │ │  "Yes"   │ │  "Yes"   │
             └────┬─────┘ └────┬─────┘ └────┬─────┘
                  │            │            │
                  └────────────┼────────────┘
                    Phase 2:   │    "All said yes -> COMMIT"
                         ┌─────▼──────┐
                         │ Coordinator │
                         └────────────┘
         (If ANY said "No" -> ROLLBACK all)
```

**Tradeoff:** Strong consistency, but slow. All participants are locked/blocked while waiting. If the coordinator crashes between phases, everything is stuck. Rarely used in modern distributed systems for this reason.

**Example designs where this shows up:**
- **Cross-bank money transfer** - debit one bank, credit another. Both must succeed or both fail.
- **Distributed database commits** - some SQL databases use 2PC internally for cross-shard transactions.
- In interviews, you're more likely to **mention why you avoid it** and prefer Saga instead.

---

## 3. Saga Pattern

**What it is:** Break a distributed transaction into a chain of local transactions, each with a **compensating action** (undo) if something fails downstream.

**Why:** Avoids the blocking problem of 2PC. Each step commits independently. If step 3 fails, you run compensating actions for steps 2 and 1.

```
  ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
  │ Order     │────►│ Payment   │────►│ Inventory │────►│ Shipping  │
  │ Service   │     │ Service   │     │ Service   │     │ Service   │
  │ (create)  │     │ (charge)  │     │ (reserve) │     │ (ship)    │
  └───────────┘     └───────────┘     └─────┬─────┘     └───────────┘
                                            │
                                         FAILS!
                                            │
                                      Compensate:
                    ┌───────────┐     ┌─────▼─────┐
                    │ Payment   │◄────│ Inventory │
                    │ (refund)  │     │ (unreserve)│
                    └─────┬─────┘     └───────────┘
                    ┌─────▼─────┐
                    │ Order     │
                    │ (cancel)  │
                    └───────────┘
```

**Two flavors:**
- **Choreography:** Each service listens for events and acts. No central controller. Simpler but harder to track.
- **Orchestration:** A central orchestrator tells each service what to do. Easier to track but single point of coordination.

**Example designs where this shows up:**
- **E-commerce order flow** - create order, charge payment, reserve inventory, schedule shipping. If inventory is out of stock, refund and cancel.
- **Travel booking** - book flight, book hotel, book car. If hotel is unavailable, cancel the flight.
- **Food delivery** - accept order, assign driver, charge customer. If no driver available, refund and cancel.

---

## 4. Replicated Load-Balanced Services (RLBS)

**What it is:** Run multiple identical copies of a stateless service behind a load balancer.

**Why:** Availability and throughput. One instance goes down, others keep serving. Need more capacity, add more instances.

```
                    ┌──────────────┐
                    │  Service (1) │
              ┌────►│  (stateless) │
              │     └──────────────┘
 ┌──────┐     │     ┌──────────────┐
 │  LB  │─────┼────►│  Service (2) │
 └──────┘     │     │  (stateless) │
              │     └──────────────┘
              │     ┌──────────────┐
              └────►│  Service (3) │
                    │  (stateless) │
                    └──────────────┘
```

**This is the most basic pattern.** You use it in every design. The API servers behind the LB in your counter, URL shortener, and rate limiter are all RLBS.

**Example designs where this shows up:**
- **Every single design** - the API server layer is always RLBS.
- **URL shortener** - stateless API servers behind LB, any server can handle any request.
- **Rate limiter** - API gateway instances behind LB (state lives in Redis, not the servers).

---

## 5. Sharded Services

**What it is:** Split data or workload across multiple instances by a key. Each instance owns a subset of the data.

**Why:** When one instance can't hold all the data or handle all the writes. Unlike RLBS where every instance is identical, each shard is **different** - it only handles its portion.

```
                    ┌────────────────┐
              ┌────►│  Shard 0       │  users A-H
              │     │  (owns subset) │
 ┌──────┐     │     └────────────────┘
 │Router│─────┤     ┌────────────────┐
 │hash()│     ├────►│  Shard 1       │  users I-P
 └──────┘     │     │  (owns subset) │
              │     └────────────────┘
              │     ┌────────────────┐
              └────►│  Shard 2       │  users Q-Z
                    │  (owns subset) │
                    └────────────────┘
```

**Key decision:** What do you shard by? (user ID, counter key, geographic region). Bad shard keys create hot spots.

**Example designs where this shows up:**
- **Distributed counter** - shard Kafka by counter key so all events for one counter go to the same partition.
- **Chat system** - shard message storage by conversation ID. All messages for one chat live on the same shard.
- **URL shortener** - shard DB by short code hash when a single DB can't handle the write volume.
- **Any NoSQL database** - Cassandra and DynamoDB shard automatically by partition key.

---

## 6. Event Sourcing + Outbox Pattern

**Event Sourcing:** Instead of storing current state, store every change as an event. Current state = replay all events.

```
  Traditional:    account_balance = $500  (just the current number)

  Event Sourced:  [deposit $1000] -> [withdraw $200] -> [withdraw $300]
                  Current balance = replay events = $500
```

**Why:** Full audit trail. Can rebuild state at any point in time. Can derive new views from the same events.

**Outbox Pattern:** Solves the problem of "I need to update my DB AND publish an event, atomically." Instead of publishing directly to Kafka (which could fail after the DB write), write the event to an "outbox" table in the same DB transaction. A separate process reads the outbox and publishes to Kafka.

```
 ┌──────────┐    single DB transaction     ┌──────────────────────┐
 │ Service  │─────────────────────────────►│  Database            │
 └──────────┘                              │  ┌────────────────┐  │
                                           │  │ Business Table │  │
                                           │  └────────────────┘  │
                                           │  ┌────────────────┐  │
                                           │  │ Outbox Table   │  │
                                           │  └───────┬────────┘  │
                                           └──────────┼───────────┘
                                                      │
                                            ┌─────────▼──────────┐
                                            │ Outbox Publisher   │
                                            │ (polls or CDC)     │
                                            └─────────┬──────────┘
                                                      │
                                                      ▼
                                                   Kafka
```

**Example designs where this shows up:**
- **Payment system** - store every transaction as an event. Full audit trail for compliance. Outbox ensures the "payment processed" event always reaches Kafka.
- **Order management** - event sourcing lets you see the full order history (created, paid, shipped, delivered, returned).
- **Notification system** - outbox pattern ensures "send notification" events are never lost even if Kafka is temporarily down.

---

## 7. Idempotency + Retries

**What it is:** Designing operations so that doing them multiple times has the same effect as doing them once.

**Why:** Networks are unreliable. A client sends a request, the server processes it, but the response is lost. Client retries. Without idempotency, you've now processed it twice (double charge, double count).

```
 ┌────────┐     POST /pay (idempotency_key: "abc123")     ┌──────────┐
 │ Client │───────────────────────────────────────────────►│ Service  │
 └────┬───┘                                                └─────┬────┘
      │                                                          │
      │  (network timeout, no response received)                 │ processes payment
      │                                                          │ stores key "abc123"
      │     POST /pay (idempotency_key: "abc123")  [RETRY]       │
      │─────────────────────────────────────────────────────────►│
      │                                                          │
      │     "abc123" already seen -> return cached result        │
      │◄─────────────────────────────────────────────────────────│
```

**How:** Client sends a unique `idempotency_key` with each request. Server checks if it's seen that key before. If yes, return the previous result without reprocessing.

**Example designs where this shows up:**
- **Payment processing** - Stripe requires idempotency keys. Retry a charge without double-charging.
- **Distributed counter (exact counts)** - the deduplication layer in the HBase counter design uses this to avoid double-counting replayed Kafka messages.
- **Order creation** - user clicks "Place Order" twice due to slow network. Only one order is created.
- **Message delivery** - chat system deduplicates messages so retries don't create duplicate messages.

---

## 8. Circuit Breaker + Bulkhead

**Circuit Breaker:** If a downstream service keeps failing, stop calling it temporarily instead of piling up timeouts.

```
 ┌──────────┐     ┌─────────────────┐     ┌──────────────┐
 │ Service A│────►│ Circuit Breaker │────►│ Service B    │
 └──────────┘     └────────┬────────┘     │ (struggling) │
                           │              └──────────────┘
                           │
              States:
              CLOSED  ──► calls pass through normally
              OPEN    ──► calls rejected immediately (fast fail)
              HALF-OPEN ─► let a few test calls through to check recovery
```

**Bulkhead:** Isolate different parts of your system so one failing dependency doesn't take down everything. Like compartments in a ship - one floods, the rest stay dry.

```
 ┌──────────────────────────────────────────┐
 │              Service A                    │
 │  ┌──────────────┐  ┌──────────────────┐  │
 │  │ Thread Pool  │  │  Thread Pool     │  │
 │  │ for DB calls │  │  for External API│  │
 │  │  (10 threads)│  │  (5 threads)     │  │
 │  └──────────────┘  └──────────────────┘  │
 └──────────────────────────────────────────┘
   If External API hangs, only its 5 threads are stuck.
   DB calls keep working fine on their own pool.
```

**Example designs where this shows up:**
- **Rate limiter** - the rate limiter itself is a circuit breaker for your backend. If a client is abusing the API, cut them off (429) before they overload the system.
- **Notification system** - if the email provider (SendGrid) is down, circuit breaker stops calling it. SMS and push notifications keep working (bulkhead isolation).
- **API gateway** - if one downstream microservice is slow, the gateway circuit-breaks it so other endpoints stay fast.
- **Any system with external dependencies** - payment providers, third-party APIs, etc.

---

## Priority for Mid-Level Interviews

### Must Know (you already use these)
- **RLBS** - You put stateless services behind a load balancer in every design. Just know the name.
- **Sharding** - Know when to shard (write-heavy, data too big for one node), how to pick shard keys, and what causes hot spots.
- **CQRS** - You already do this every time you separate read/write paths with different stores. Just know the name.

### Good to Know (mention when relevant)
- **Saga** - Know the concept and the two flavors (choreography vs orchestration). Mention when a design involves multi-service transactions (e-commerce, booking).
- **Idempotency** - Mention for any system where duplicate requests are dangerous (payments, orders, message delivery).

### Just Be Aware (don't need to deep dive)
- **Circuit Breaker / Bulkhead** - Mention during fault tolerance discussion. "If this external service goes down, we circuit-break it so the rest of the system stays healthy."
- **2PC** - Know why it's bad (blocking, coordinator is SPOF). If asked about distributed transactions, say you'd prefer Saga.
- **Event Sourcing / Outbox** - Senior territory. Mention if the interviewer asks about audit trails or guaranteed event delivery.

---

## 9. PACELC Theorem (NFR Decision Framework)

**What it is:** An extension of CAP that covers both failure AND normal operation.

- **CAP** says: during a network **P**artition, pick **A**vailability or **C**onsistency.
- **PACELC** adds: **E**lse (normal operation), pick **L**atency or **C**onsistency.

```
If Partition:
  choose Availability or Consistency  (PA or PC)
Else (normal operation):
  choose Latency or Consistency  (EL or EC)
```

**The EL tradeoff matters:** Picking "Latency" in normal operation means "return fast even if the data might be stale." That's eventual consistency. The system responds quickly but you might read a value that hasn't been updated yet. This isn't just a failure-mode thing - it's how the system behaves all the time.

| System | During Partition | Normal Operation | What it means |
|---|---|---|---|
| Cassandra, DynamoDB | Availability | Latency | Always fast, always available. Reads may be stale. Eventual consistency. |
| PostgreSQL, MySQL | Consistency | Consistency | Always correct. Slower. Rejects requests if it can't guarantee consistency. |
| Redis (replicated) | Availability | Latency | Fast reads from replicas, but replica may lag behind primary. |

**How this connects to your designs:**
- Distributed counter with Cassandra = PA/EL. "Reads can be a few seconds stale, and that's fine for page views."
- Exact counter with PostgreSQL = PC/EC. "Every read must be accurate because it's financial data."
- Rate limiter with Redis = PA/EL. "Slightly over-counting (62 instead of 60) is acceptable."

**Interview tip:** You don't need to say "PACELC." Just say "I chose Cassandra because we prioritized availability and low latency over strong consistency" - that's the same thing in plain English.
