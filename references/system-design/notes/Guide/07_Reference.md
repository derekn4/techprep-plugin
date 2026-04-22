# Step 7: Deep Dive Reference

> **Goal:** When the interviewer picks an area to go deep on, use these comparisons to explain tradeoffs confidently.

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

## HyperLogLog

Probabilistic data structure that estimates unique counts using ~12KB of memory regardless of set size (~98% accurate).

**Use when:** The interviewer says "unique" or "distinct" at scale (unique visitors, distinct users). Regular counters are for total counts.

**Redis has it built in:** `PFADD key element`, `PFCOUNT key`.

**Interview phrasing:** "For counting unique users at this scale, I'd use HyperLogLog in Redis. It gives us ~98% accuracy with only 12KB of memory, which is a worthwhile tradeoff vs storing every user ID."
