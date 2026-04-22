# Step 4: API Design - ROPES

> **Goal:** Define how clients talk to your system. ~3 minutes.

---

## The Checklist

- **R** - Resources (what are the entities/nouns? `/tasks`, `/users`, `/messages`)
- **O** - Operations (what HTTP verbs per resource? GET, POST, PUT, DELETE)
- **P** - Payloads (request body/query params, response shape, what fields?)
- **E** - Errors (status codes: 400 bad input, 404 not found, 429 rate limited, 500 server error)
- **S** - Specials (pagination, auth, rate limiting, versioning, idempotency keys)

You don't need to design a full API spec in the interview. State the resources, list 3-4 key endpoints with their verbs, and mention one or two specials that matter for the problem (e.g., "pagination on GET /messages" or "idempotency key on POST /payments").

**Target: Focus on R, O, S. Keep P and E light.**
- **Resources + Operations** (the core): Name your resources, list 3-4 key endpoints with their HTTP verbs. This is what matters.
- **Specials** (1-2 that are relevant): Mention pagination if there's a list endpoint, idempotency keys if there are payments/writes that can't be duplicated, rate limiting if abuse is a concern. Don't list all of them -- just the ones that matter for this problem.
- **Payloads** (keep light): Mention the key fields inline with the endpoint -- "POST body includes `callback_url` and `scheduled_at`." Don't define full schemas or types.
- **Errors** (skip unless relevant): Don't enumerate status codes. Only mention one if it's design-relevant -- "429 for rate limiting" or "409 for dedup conflicts." The interviewer doesn't care that you know 404 exists.

---

## Example (Task Scheduler)

```
POST   /tasks          - schedule a new task (body: callback_url, payload, scheduled_at)
GET    /tasks/{id}     - check task status (response: status, retry_count, scheduled_at)
DELETE /tasks/{id}     - cancel a pending task
GET    /tasks?service_id=X&status=failed  - list failed tasks for a service (paginated)
```

---

## Pagination (the Most Common "Special")

Pagination is how you return large result sets in chunks instead of all at once.

**Offset-based** (simpler):
```
GET /messages?offset=0&limit=20     -> first 20
GET /messages?offset=20&limit=20    -> next 20
```
Downside: if new data gets inserted while you're paging, you can skip or duplicate items.

**Cursor-based** (better for real-time data):
```
GET /messages?cursor=msg_abc123&limit=20
```
The cursor is the ID or timestamp of the last item you received. Server returns everything after that point. No skipping/duplicating even if new data comes in.

**Which to pick:** Cursor-based for feeds/timelines/chat (data changes frequently). Offset-based for simpler things like admin dashboards or search results.

---

## API Design for Non-REST Protocols

ROPES is REST-focused, but most systems have a REST API for CRUD plus another protocol for real-time or async. Define both during this phase.

**General principle:** The same core question applies regardless of protocol -- "what can clients do and how?" What changes is the format.

### WebSocket Events (Chat, Collaborative Editing, Multiplayer)

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

**Most chat/real-time systems need both REST and WebSocket APIs:**
- **REST** for CRUD that doesn't need real-time: create account, fetch message history, update profile
- **WebSockets** for real-time events: send/receive messages, typing indicators, presence

### Kafka / Event-Driven (Service-to-Service)

Define **topic names** and **event schemas**. These aren't client-facing -- they're how your internal services communicate.

```
Topic: chat.messages      -> { message_id, chat_id, sender_id, text, timestamp }
Topic: user.presence      -> { user_id, status, timestamp }
Topic: notifications.send -> { user_id, type, title, body, channel }
```

### gRPC (Service-to-Service)

Define **service methods**. Rarely needed in interviews unless they ask about inter-service communication.

```
service ChatService {
  rpc SendMessage(SendRequest) returns (SendResponse);
  rpc StreamMessages(StreamRequest) returns (stream Message);
}
```

### Quick Decision: Which API(s) to Define

| System type | Define during API phase |
|---|---|
| Standard CRUD (URL shortener, task scheduler) | REST only |
| Real-time + CRUD (chat, dashboard, collab editing) | REST + WebSocket events |
| Async processing (notification pipeline, analytics) | REST + Kafka topics |
| Full combo (chat with notifications) | REST + WebSocket events + Kafka topics |
