# System Design Mental Model

## Core Principle: Trace the Request Lifecycle

Don't try to recall components from memory. Instead, **trace a single user request from start to finish**. Every system design is really just answering: *what happens when a user does X?*

---

## Step 1: Entry Point — How does the request get in?

- Client (mobile, web, API)
- DNS / CDN (if serving static content or global users)
- Load Balancer

## Step 2: Processing — Who handles the logic?

- API Gateway / Web Server
- Application Service(s) — break into microservices if different domains (e.g., user service, payment service, feed service)
- Ask: does this need to be synchronous or asynchronous?

## Step 3: Data — Where does state live?

- Database (SQL vs NoSQL — driven by your access patterns)
- Cache (Redis/Memcached — for hot reads)
- Ask: read-heavy or write-heavy? This drives your storage choices.

## Step 4: Communication — How do components talk?

### Service-to-Service

- Synchronous: REST / gRPC between services
- Asynchronous: Message queue (Kafka, SQS) for decoupling, handling spikes, or eventual consistency

### Server-to-Client (Real-Time)

Ask: **Who initiates the data flow?**

| Pattern | Direction | When to Use |
|---|---|---|
| HTTP (REST/gRPC) | Client pulls | Standard request-response. Client asks, server responds. |
| WebSockets | Bidirectional | Client AND server need to push data to each other. Chat, multiplayer games, collaborative editing. |
| SSE (Server-Sent Events) | Server pushes | Only server needs to push. Live dashboards, notifications, activity feeds. Simpler than WebSockets. |
| Long Polling | Client pulls (frequent) | Fallback when WebSockets/SSE aren't supported. Client repeatedly asks "anything new?" |

### WebSocket Architecture Concerns

WebSockets introduce **statefulness** into an otherwise stateless architecture. This creates specific design challenges:

- **Connection Management** — WebSocket connections are persistent TCP connections. Users are pinned to a specific server instance, unlike stateless HTTP.
- **Fanout Problem** — If User A sends a message and User B is on a different server, you need a **pub/sub layer** (Redis Pub/Sub, Kafka) so WebSocket servers can relay messages across instances.
- **Scaling** — Can't just load-balance and forget. Need sticky sessions or a **connection registry** (mapping user → which WS server they're on).
- **Fallback** — Mention long-polling or SSE as fallbacks when WebSockets aren't supported.

## Step 5: Scaling & Reliability — What breaks at scale?

- Horizontal scaling, replication, sharding
- Rate limiting, circuit breakers
- Monitoring / logging

---

## Forcing Questions Checklist

When you feel stuck after gathering requirements, ask yourself these questions. Each one drives you toward specific components:

| Question | What It Drives |
|---|---|
| What's the core entity? (URL, message, video, post) | Data model |
| What are the access patterns? (read-heavy? write-heavy?) | DB choice + caching strategy |
| What needs to be real-time vs. eventual? | Sync vs async, WebSockets vs queues |
| Does the client need real-time server-pushed updates? | WebSockets (bidirectional) or SSE (server→client), plus pub/sub for fanout |
| What's the scale? (QPS, storage) | Partitioning, caching, CDN |
| What's the single point of failure? | Redundancy decisions |

---

## Interview Tip

After gathering requirements, say something like:

> *"Let me walk through the lifecycle of a [core action]. A user sends a request, it hits our load balancer, routes to our application server, which needs to read/write from our data store..."*

This gives you a skeleton on the whiteboard immediately. Then layer on complexity based on the non-functional requirements (scale, latency, availability) you gathered.

You're not recalling a list of components — you're **deriving** them from the problem. That shows you understand *why* each piece exists.
