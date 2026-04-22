# Step 5: Database Design - TABLE

> **Goal:** Decide how data is stored and queried. ~5 minutes.

---

## The Checklist

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

---

## Example (Task Scheduler)

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

## How to Think About Indexes

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
