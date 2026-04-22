# System Design: Chat Application (Millions of Users)

**Pattern:** WebSockets (bidirectional real-time) + REST + Event-Driven

---

## Overview

Design a chat system that supports 1:1 messaging and group chats for millions of concurrent users with real-time message delivery. The core challenges: **how do you deliver messages in real-time across distributed servers, guarantee delivery, and maintain message ordering at scale?**

---

## Clarifying Questions & Answers

| Question | Answer |
|----------|--------|
| 1:1 only, or group chats too? | Both. Groups up to ~500 members. |
| How many total users? | ~100M registered, ~10M concurrent |
| Do we need read receipts / typing indicators? | Yes (ephemeral signals, don't need to persist) |
| Do we need media (images, files)? | Yes, but focus on text first, media as extension |
| Message history - how long do we keep it? | Forever (users expect to scroll back) |
| Do messages need to be delivered if user is offline? | Yes - store and deliver when they reconnect |
| End-to-end encryption? | Out of scope for this design (mention it exists) |
| Do we need presence (online/offline status)? | Yes |
| What's the acceptable delivery latency? | Sub-second for online users |
| Multi-device support? | Yes - user can be on phone + desktop simultaneously |

---

## Requirements

### Functional
- **Send message** to a user or group
- **Receive messages** in real-time
- **Message history** - paginated, scrollable
- **Group chats** - create, add/remove members, up to 500 members
- **Online/offline presence** indicators
- **Read receipts** and **typing indicators**
- **Media sharing** (images, files)
- **Multi-device sync** - same user on multiple devices

### Non-Functional
- **Low latency:** Sub-second message delivery for online users
- **Reliability:** Messages must never be lost (at-least-once delivery)
- **Ordering:** Messages appear in correct order within a conversation
- **Scalability:** 10M concurrent WebSocket connections
- **Availability:** Always up - chat is a core feature
- **Durability:** Message history persisted permanently

---

## High-Level Design

```
                                    ┌──────────────┐
                                    │  Media Store  │
                                    │  (S3 / CDN)   │
                                    └──────────────┘

Client A ──WS──┐
Client B ──WS──┤    ┌────────┐    ┌──────────────────┐
Client C ──WS──┼───►│   LB   │───►│   Chat Service   │
Client D ──WS──┤    │(sticky)│    │   (WS Servers)   │
Client E ──WS──┘    └────────┘    └────────┬─────────┘
                                           │
                          two things happen in parallel:
                                           │
                        ┌──────────────────┼──────────────────┐
                        │ INSTANT DELIVERY │                   │ ASYNC WORK
                        ▼                  │                   ▼
                ┌───────────────┐          │          ┌───────────────┐
                │ Redis Pub/Sub │          │          │     Kafka     │
                │ + Connection  │          │          │  (per-conv    │
                │   Registry    │          │          │   partitions) │
                └───────┬───────┘          │          └───────┬───────┘
                        │                  │                  │
                        ▼                  │                  ▼
                Other WS Servers           │          ┌───────────────┐
                        │                  │          │    Workers    │
                        ▼                  │          └──┬─────┬──┬──┘
                   User B sees             │             │     │  │
                   message (~1ms)          │             ▼     ▼  ▼
                                           │      ┌──────┐ ┌────┐ ┌──────┐
                                           │      │Cassan│ │User│ │ Push │
                                           │      │-dra  │ │Cash│ │ Notif│
                                           │      │(DB)  │ │Redis│ │(APNs│
                                           │      └──────┘ └────┘ │/FCM)│
                                           │                      └──────┘

REST endpoints (non-real-time operations):
Client --REST--> LB -> API Gateway -> User Service -> User DB (Postgres)
                                   -> Group Service -> Group DB (Postgres)
                                   -> History Service -> Message DB (Cassandra)
```

---

## Data Flow

### Send a Message (1:1)

```
1. Client A sends message over WebSocket connection (NOT REST - connection is already open)
   { to: "user_B", text: "hey", msg_id: "uuid-123", timestamp: ... }

2. WS Server receives it, validates, assigns server timestamp + sequence number

3. Ack back to Client A over WebSocket: "message accepted"
   (Client A shows checkmark: "sent")

4. WS Server splits into TWO PARALLEL paths:

   PATH A - INSTANT DELIVERY (Pub/Sub, ~1ms):
      a. Look up connection registry: "Where is User B connected?"
      b. If User B is ONLINE:
         - Publish to Redis Pub/Sub channel for User B's WS server
         - That WS server pushes message to User B over WebSocket
         - User B sees the message instantly
         - User B's client acks receipt -> "delivered" checkmark on Client A

   PATH B - ASYNC WORK (Kafka, runs in parallel, nobody waits for this):
      a. Write to Kafka (topic partitioned by conversation_id)
      b. Message Worker consumes from Kafka:
         - Persist to Cassandra (durable storage)
         - Update unread counts in cache
         - If User B is OFFLINE: trigger push notification (APNs / FCM)
         - When User B reconnects, deliver all queued messages from DB

Why two paths? Pub/Sub is instant but fire-and-forget (no persistence).
Kafka is durable but adds latency. Use pub/sub for delivery, Kafka for
everything that can happen a few seconds later.
```

### Send a Message (Group Chat)

```
Same parallel split as 1:1, but Path A fans out to ALL group members:

PATH A - INSTANT DELIVERY:
   - For each online member: push via Redis Pub/Sub -> WS Server -> Client
   - Optimization for large groups:
     - Don't fan out to 500 connections individually
     - Publish ONCE to a group channel in Redis Pub/Sub
     - Each WS server that has group members subscribed receives it
     - WS server pushes to all local group members

PATH B - ASYNC WORK (same as 1:1):
   - Kafka -> Workers -> persist to DB
   - Send push notifications to offline members
```

### Retrieve Message History

```
Client --REST GET--> API Gateway -> History Service -> Cassandra
  GET /conversations/{conv_id}/messages?before={timestamp}&limit=50

- Paginated by timestamp (cursor-based pagination)
- Most recent messages served from Redis cache (hot data)
- Older messages from Cassandra (cold data)
```

---

## Deep Dive

### 1. WebSocket Connection Management (The Core Challenge)

**Problem:** 10M concurrent connections across many servers. How do you know which server a user is connected to?

**Connection Registry (Redis):**
```
Key: "conn:user_B"
Value: { server_id: "ws-server-42", connected_at: ..., devices: ["phone", "desktop"] }
```

- When user connects, register in Redis
- When user disconnects (or heartbeat timeout), remove from Redis
- TTL on keys as safety net (if server crashes without cleanup)

**Multi-device:** User B has phone + desktop. Both have WS connections, possibly to different servers. Connection registry stores a list of connections per user. Message gets pushed to ALL active devices.

**Heartbeats:** Client sends ping every 30 seconds. If server doesn't receive ping for 90 seconds, consider connection dead, clean up registry.

### 2. Cross-Server Message Delivery (Pub/Sub Fanout)

**Problem:** User A is on WS Server 1, User B is on WS Server 5. How does the message get there?

**Redis Pub/Sub approach:**
- Each WS server subscribes to channels for all users connected to it
- To deliver to User B: publish to channel `user:B`
- WS Server 5 (subscribed to `user:B`) receives it and pushes over WebSocket

**Why Redis Pub/Sub and not Kafka for this?**
- Redis Pub/Sub is fire-and-forget, very low latency (sub-ms)
- We already persisted the message to Kafka/DB, so durability is handled
- If the pub/sub message is lost (user disconnected mid-delivery), the undelivered queue catches it
- Kafka is overkill for ephemeral delivery signals

**At very large scale (10M+ connections):**
- Single Redis instance can't handle all pub/sub traffic
- Shard Redis Pub/Sub by user_id hash
- Or use a dedicated pub/sub system (e.g., NATS)

### 3. Message Ordering

**Problem:** Messages arrive out of order due to network latency, multiple servers, etc.

**Solution: Kafka partitioning by conversation_id**
- All messages for a conversation go to the SAME Kafka partition
- Kafka guarantees ordering within a partition
- Assign monotonically increasing sequence numbers per conversation

**Client-side ordering:**
- Each message has a `sequence_number` within its conversation
- Client renders messages sorted by sequence number, not arrival time
- If message 5 arrives before message 4, client buffers and waits briefly

### 4. Offline Message Delivery

**Problem:** User B is offline when User A sends a message.

```
Message Worker checks connection registry:
  User B not found -> OFFLINE

  1. Store message in "undelivered" queue (Redis list or DB table)
     Key: "undelivered:user_B"
     Value: [msg_1, msg_2, msg_3, ...]

  2. Send push notification via APNs (iOS) / FCM (Android)
     "User A: hey"

  3. When User B reconnects (WebSocket handshake):
     a. WS Server checks undelivered queue
     b. Delivers all queued messages in order
     c. Clears the queue
     d. Registers User B in connection registry
```

### 5. Presence (Online/Offline Status)

**Problem:** Show green dot for online users. But with 10M users, broadcasting every status change is expensive.

**Approach: Lazy presence with heartbeats**
- User sends heartbeat every 30s -> update Redis: `presence:user_B = {last_seen: timestamp}`
- To check if User B is online: `last_seen` within last 90 seconds = online
- Don't broadcast status changes globally - only check when a user opens a conversation

**For group chats:**
- When user opens a group chat, client requests presence for all members
- Server checks Redis for each member's `last_seen`
- Subscribe to presence changes only for visible group members (not all users)

### 6. Typing Indicators & Read Receipts

**Typing indicators (ephemeral, no persistence):**
- Client sends `{type: "typing", conv_id: "..."}` over WebSocket
- WS server publishes directly via Redis Pub/Sub to other participants
- No Kafka, no DB - this is throwaway data
- Throttle to max 1 typing event per 3 seconds

**Read receipts (persisted):**
- Client sends `{type: "read", conv_id: "...", up_to_seq: 47}` over WebSocket
- Persist to DB: `last_read[user_B][conv_id] = 47`
- Notify other participants via pub/sub

### 7. Media (Images, Files)

```
1. Client uploads file via REST (not WebSocket - large payloads)
   POST /upload -> API Gateway -> Media Service -> S3

2. S3 returns URL. Media Service generates thumbnail.

3. Client sends chat message with media reference:
   { text: "", media_url: "s3://bucket/img123", media_type: "image" }

4. Receiving client downloads media from CDN (S3 fronted by CloudFront)
```

**Why not send media over WebSocket?** WebSockets are for small, frequent messages. Large binary uploads would block the connection. REST with multipart upload is better suited.

### 8. Database Choice

**Messages: Cassandra**
- Write-optimized (LSM-tree) - handles high message volume
- Natural time-series model: partition by `conversation_id`, cluster by `timestamp`
- Horizontally scalable, no single point of failure
- Schema:
  ```
  Table: messages
  Partition key: conversation_id
  Clustering key: sequence_number (ascending)
  Columns: sender_id, text, media_url, created_at, message_id
  ```

**Users, Groups, Contacts: PostgreSQL**
- Relational data with JOINs (group membership, contacts)
- Strong consistency (user profile updates must be immediately visible)
- Lower write volume than messages

**Cache: Redis**
- Recent messages per conversation (last 50)
- Connection registry
- Presence data
- Undelivered message queues

---

## Scaling Considerations

### How many WS servers do we need?
- A single server can hold ~50K-100K concurrent WebSocket connections
- 10M concurrent users / 50K per server = **~200 WS servers**
- Multi-device (avg 1.5 devices per user) = ~300 servers

### Load Balancer Configuration
- **Sticky sessions** (by user_id) - user stays on same WS server for the connection lifetime
- Layer 4 (TCP) load balancing, not Layer 7 (HTTP) - WebSocket is a long-lived TCP connection
- Health checks on WS servers - if a server dies, affected users reconnect to a new server

### Hot Groups (Viral group chat with 500 active members)
- Fan-out optimization: publish once to group channel, not 500 individual channels
- If all 500 members are on different servers, that's 500 pub/sub deliveries per message
- For extremely hot groups: dedicated WS server for that group's members (route at LB level)

### Multi-Region
```
Region A (US)                     Region B (EU)
  WS Servers + Redis                WS Servers + Redis
  Kafka cluster                     Kafka cluster
  Cassandra (local DC)              Cassandra (local DC)
         \                         /
          -- Async replication --
```
- Users connect to nearest region (geo-DNS routing)
- Cross-region messages: replicate via Kafka MirrorMaker or Cassandra multi-DC replication
- Tradeoff: cross-region messages have higher latency (~100-200ms extra)

---

## Key Tradeoffs to Discuss

| Decision | Tradeoff |
|----------|----------|
| WebSockets vs Long Polling | WS gives true real-time + lower overhead, but adds statefulness + sticky session complexity |
| Redis Pub/Sub vs Kafka for delivery | Redis is faster but fire-and-forget. Kafka is durable but higher latency. Use Redis for delivery, Kafka for persistence. |
| Cassandra vs PostgreSQL for messages | Cassandra handles write volume and scales horizontally, but no ACID transactions and harder to operate. Postgres is simpler but needs sharding at scale. |
| Fan-out on write vs on read (groups) | Write: pre-deliver to all members (fast reads, expensive writes). Read: deliver on demand (cheap writes, slower reads). For groups <500, fan-out on write is fine. |
| Presence: push vs pull | Push (broadcast every change): expensive at scale. Pull (check on demand): slight delay but much cheaper. Hybrid: push within open conversations, pull otherwise. |
| Message ordering: server vs client | Server-assigned sequence numbers are authoritative, but client must handle out-of-order arrival gracefully |

---

## Email / Collaboration Product Angle

If they frame it as email/communication-related, think:
- **Real-time email notifications** - new email arrives, push to all user devices instantly
- **Collaborative email threads** - multiple team members replying/commenting on same thread
- **Shared inbox** - team members see updates in real-time (someone claimed a ticket, started replying)
- **AI-assisted drafts** - server pushes AI suggestions to client in real-time as user types

Same WebSocket + Pub/Sub + Connection Registry architecture applies. The difference is the data model (email threads vs chat conversations) and the delivery semantics (email is inherently async-tolerant, chat demands real-time).
