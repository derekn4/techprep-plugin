# Data Fundamentals

**Purpose:** Solid data fundamentals are a strong signal in system design interviews. Even when other parts of your design are weak, demonstrating data competence (modeling, sharding, scaling) shows you're capable of working on real data-heavy systems.

**Key insight:** Many companies use the same system design loop regardless of whether the role is backend or data-focused. If you're being routed toward a data-oriented team, showing data competence gives you an extra edge.

---

## Sharding

**What:** Splitting a database across multiple machines so each holds a subset of data.

**Why:** Single DB can't handle the write throughput or storage at scale.

### Sharding Strategies

**1. Hash-based sharding**
```
shard = hash(user_id) % num_shards
```
- Even distribution
- Can't do range queries across shards efficiently
- Adding shards requires rehashing (use consistent hashing to minimize)

**2. Range-based sharding**
```
Shard 1: user_id 1-1M
Shard 2: user_id 1M-2M
```
- Supports range queries within a shard
- Risk of hot spots (if recent users are most active, last shard gets hammered)

**3. Directory-based sharding**
- Lookup service maps key → shard
- Most flexible, but lookup service is a single point of failure
- Can rebalance without changing application logic

### Shard Key Selection (Critical Decision)

Pick a key that:
- **Distributes evenly** (avoid hot spots)
- **Aligns with query patterns** (queries should hit 1 shard, not all)
- **Rarely changes** (re-sharding is expensive)

| System | Good Shard Key | Why |
|--------|---------------|-----|
| Social feed | user_id | Queries are per-user, even distribution |
| Analytics | timestamp + event_type | Time-series, queries are by time range |
| Chat | conversation_id | Messages queried per conversation |
| E-commerce | order_id or user_id | Depends on primary access pattern |

### Problems with Sharding
- **Cross-shard queries** are slow (scatter-gather)
- **Cross-shard transactions** are very hard (2PC, Saga pattern)
- **Joins across shards** don't work → denormalize
- **Rebalancing** when adding shards is operationally complex

---

## Partitioning

**What:** Dividing a table's data within a single database instance. Often confused with sharding, but partitioning is within one DB.

### Types

**1. Horizontal Partitioning (most common)**
Split rows across partitions.
```sql
-- PostgreSQL example: partition by date range
CREATE TABLE events (
    id BIGINT,
    user_id INT,
    occurred_at TIMESTAMP,
    event_type TEXT
) PARTITION BY RANGE (occurred_at);

CREATE TABLE events_2026_01 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE events_2026_02 PARTITION OF events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```
- Queries with `WHERE occurred_at = ...` only scan relevant partition
- Old data easily archived by dropping old partitions
- Common for time-series, logs, events

**2. Vertical Partitioning**
Split columns across tables.
```
users_core: id, username, created_at (hot, queried often)
users_profile: id, bio, avatar_url, preferences (cold, queried rarely)
```
- Keeps hot data small and fast
- Cold data doesn't slow down core queries

### When to Partition
- Table has millions+ rows and queries are slow
- Clear access pattern by time, region, or category
- Need to archive/drop old data easily
- Single table scans are becoming bottleneck

---

## Relational Modeling (Practical Walkthrough)

### The Process: How to Model Any System

**Step 1: Identify entities** - What are the "things" in your system?
**Step 2: Identify relationships** - How does entity A relate to entity B?
**Step 3: Turn it into tables** - Each entity = table, each many-to-many = junction table

### Full Example: Social Media Posts

**Step 1 - Entities:** Users, Posts, Tags, Media

**Step 2 - Relationships:**
- User authors many posts → **one-to-many**
- Post can have many tags, tag can be on many posts → **many-to-many** (needs junction table)
- User follows many users, user is followed by many → **many-to-many** (self-referencing)
- Post can have many media items (images, video) → **one-to-many**

**Step 3 - Tables:**
```sql
-- Entity tables
users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(100) UNIQUE,
    created_at  TIMESTAMP
)

posts (
    id          SERIAL PRIMARY KEY,
    author_id   INT REFERENCES users(id),   -- FK: who posted
    body        TEXT,
    created_at  TIMESTAMP
)

tags (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) UNIQUE          -- "#travel", "#food"
)

media (
    id          SERIAL PRIMARY KEY,
    post_id     INT REFERENCES posts(id),   -- FK: which post
    url         VARCHAR(500),               -- S3 link
    kind        VARCHAR(10)                 -- "image" | "video"
)

-- Junction tables (many-to-many relationships)
post_tags (
    post_id     INT REFERENCES posts(id),
    tag_id      INT REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
)

follows (
    follower_id INT REFERENCES users(id),
    followee_id INT REFERENCES users(id),
    PRIMARY KEY (follower_id, followee_id)
)
```

**Why this works:**
- **No duplicated data** - author's name lives in `users` once, not copied into every post
- **Easy to query** - "Get all posts tagged #travel" = JOIN posts → post_tags → tags
- **Easy to update** - User changes username? Update one row in `users`
- **Data integrity** - Foreign keys prevent orphaned records

### Normalization (Reducing Redundancy)

**1NF:** No repeating groups, atomic values
**2NF:** No partial dependencies (every non-key column depends on the full PK)
**3NF:** No transitive dependencies (non-key columns don't depend on other non-key columns)

The post schema above is already in 3NF. Each non-key column depends only on its table's primary key.

### Denormalization (Adding Redundancy for Speed)

**When:** Read performance matters more than write consistency.

**The problem:** "Get user's home feed" requires JOINing multiple tables:
```sql
SELECT p.* FROM posts p
JOIN follows f ON p.author_id = f.followee_id
JOIN post_tags pt ON p.id = pt.post_id
JOIN tags t ON pt.tag_id = t.id
WHERE f.follower_id = 42
ORDER BY p.created_at DESC LIMIT 50;
```
With billions of posts and fanouts across millions of followers, this is slow.

**The fix:** Create a denormalized read-optimized feed table (fan-out-on-write):
```sql
user_feed (
    user_id     INT,
    post_id     INT,
    author_name VARCHAR(100),   -- duplicated from users table
    snippet     VARCHAR(200),   -- first 200 chars of body
    created_at  TIMESTAMP,
    tags        TEXT[],         -- array of tag names
    PRIMARY KEY (user_id, post_id)
)
```

Now "get feed" is one fast query with zero JOINs:
```sql
SELECT * FROM user_feed WHERE user_id = 42 ORDER BY created_at DESC LIMIT 50;
```

**How to explain the tradeoff in an interview:**
> "I'm duplicating author_name and the post body snippet into this table, which means writes are more complex — when a user posts, I fan out writes to `user_feed` for every follower. But reads are 10x faster because I avoid several JOINs and a potentially huge fan-in at read time. For a social feed where reads massively outnumber writes, this tradeoff makes sense."

### When to Normalize vs Denormalize

| Normalize | Denormalize |
|-----------|-------------|
| Data integrity is critical | Read speed is critical |
| Write-heavy workload | Read-heavy workload |
| Data changes frequently | Data rarely changes |
| Storage is a concern | Can afford extra storage |
| OLTP (transactions) | OLAP (analytics) |

**Rule of thumb:** Start normalized, denormalize specific hot paths when needed.

### Practice: Model These Systems (Interview Exercise)

Try identifying entities → relationships → tables for:

**Notification system:**
- Entities: Users, Notifications, NotificationPreferences
- Key relationship: User receives many notifications (one-to-many)
- Shard key: user_id (queries are always "get MY notifications")

**Chat application:**
- Entities: Users, Conversations, Messages, ConversationMembers
- Key relationship: Conversation has many members (many-to-many junction)
- Shard key: conversation_id (messages queried per conversation)

---

## NoSQL Modeling (Access-Pattern-Driven)

With SQL, you model **entities and relationships**. With NoSQL, you model **access patterns**. There are no joins, so you structure data so each query hits one partition.

### SQL vs NoSQL Modeling

| | SQL (Relational) | NoSQL (Cassandra/DynamoDB) |
|---|---|---|
| Design starts with | Entities and relationships | Access patterns (queries) |
| Schema | Normalize, add junction tables | Denormalize upfront, duplicate data across tables |
| Joins | Yes, that's the point | No joins. If you need data together, store it together. |
| Example | `posts` + `post_tags` + JOIN | One table: `user_feed` with everything pre-joined |

### NoSQL Schema = Query Shape

All you need is a partition key, a sort key, and the attributes your query returns:

```
Table: user_feed
  Partition key: user_id        (which partition to look in)
  Sort key: created_at          (ordering within that partition)
  Attributes: post_id, author_name, snippet, tags, ...

Query: "get user X's recent feed items"
  → hits ONE partition, sorted by time, zero joins
```

### More Examples

```
Table: post_likes
  Partition key: post_id
  Sort key: user_id
  → "has user Y liked post X?" = single partition lookup

Table: notifications
  Partition key: user_id
  Sort key: created_at
  Attributes: type, title, body, read_status
  → "get user X's recent notifications" = single partition, sorted

Table: url_mappings
  Partition key: short_code
  Attributes: original_url, created_at, expires_at
  → "resolve short URL" = single key lookup
```

### When to Pick NoSQL Over SQL

| Pick NoSQL when... | Pick SQL when... |
|---|---|
| Access pattern is simple (get by key, sort by time) | You need joins across entities |
| Write-heavy workload | You need transactions (ACID) |
| Need horizontal scaling out of the box | Data has complex relationships |
| No joins needed | Consistency is critical |
| Schema might evolve (flexible attributes) | Schema is well-defined and stable |

### The One-Liner for Interviews

> "I'd use NoSQL here because the access pattern is simple - get by partition key, sort by time. No joins needed, and it scales writes horizontally."

---

## Modeling Data at Large Scale (Practical)

### The Scaling Playbook: What to Do When Your Schema Breaks

A normalized schema works perfectly at small scale. Here's the progression as you grow:

```
Step 1: Add indexes         (thousands of rows → millions)
Step 2: Add read replicas   (read load too high for one DB)
Step 3: Add caching         (same queries repeated constantly)
Step 4: Denormalize         (JOINs too slow on hot paths)
Step 5: Partition tables    (single tables too large to scan)
Step 6: Shard the database  (single DB instance can't handle it)
```

Don't jump to step 6 before trying step 1. Each step handles 10-100x more load.

### Step-by-step walkthrough (applied to a social feed)

**Step 1: Indexes** (handles up to ~10M rows per table)
```sql
-- Index the columns you WHERE and JOIN on
CREATE INDEX idx_posts_user_date ON posts(author_id, created_at DESC);
-- Composite index: "get user's recent posts" scans one index, not the whole table
```

Index types:
- **B-tree:** Default, good for equality AND range queries (`=`, `<`, `>`, `BETWEEN`)
- **Hash:** Only equality, faster for exact lookups (`=` only)
- **GIN:** Full-text search, JSONB queries (PostgreSQL)
- Don't over-index: each index slows down writes

**Step 2: Read replicas** (handles read-heavy load)
```
Writes → Primary DB
Reads  → Read Replica 1, Replica 2, Replica 3
```
- Scale reads horizontally by adding more replicas
- Slight replication lag (reads may be milliseconds behind)
- A social feed is very read-heavy → replicas help a lot

**Step 3: Caching** (eliminates repeated DB queries)
```
App → Check Redis cache → Cache miss? → Query DB → Store in Redis → Return
```
- Cache frequent queries: user's home feed, unread count, trending tags
- Invalidation strategies:
  - **Cache-aside (most common):** App checks cache first, fills from DB on miss
  - **TTL:** Expire after N seconds (simplest, tolerates some staleness)
  - **Write-through:** Update cache on every write (consistent but slower writes)

**Step 4: Denormalize** (eliminate expensive JOINs)
- Create `user_feed` table (see Denormalization section above)
- Write to both normalized AND denormalized tables on each post publish (fan-out-on-write)
- Read from denormalized table for speed

**Step 5: Partition** (tables too large even with indexes)
```sql
-- Partition the denormalized table by month
CREATE TABLE user_feed (...) PARTITION BY RANGE (created_at);
CREATE TABLE user_feed_2026_01 PARTITION OF user_feed
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```
- "Recent feed items" query only scans latest partition
- Old partitions archived or moved to cold storage

**Step 6: Shard** (single DB instance maxed out)
```
Shard by user_id:
  Shard 0: users 1-10M      → DB instance us-east-1
  Shard 1: users 10M-20M    → DB instance us-east-2
  Shard 2: users 20M-30M    → DB instance us-west-1
```

**The full picture at scale:**
```
50M users
  → SHARD by user_id (split across DB instances)
    → Within each shard, PARTITION by date (split within one DB)
      → Within each partition, INDEX on (user_id, created_at)
        → Redis CACHE in front for hot queries
          → READ REPLICAS for scaling read load per shard
```

**What to say in an interview:**
> "I'd start with a normalized PostgreSQL schema with proper indexes. As we scale, I'd add read replicas and Redis caching first - that handles most growth. If JOINs become a bottleneck on hot paths, I'd denormalize those specific queries. At 50M+ users, I'd shard by user_id since all queries are per-user, and partition large tables by date since users mostly access recent data."

This shows you understand the PROGRESSION, not just the end state.

### CQRS (Command Query Responsibility Segregation)

The denormalization approach above is actually a form of CQRS:
- **Write model:** Normalized tables (optimized for consistency and correctness)
- **Read model:** Denormalized `user_inbox` table (optimized for speed)
- **Sync:** On each write, update both models

Good for systems where read and write patterns are very different (social feeds: simple writes, complex fan-out reads).

### Data Pipeline Pattern (Relevant to Data Team)

```
Source Systems → Ingestion (Kafka) → Processing (batch/stream) → Storage (warehouse) → Serving (API/dashboard)
```

| Stage | Tools |
|-------|-------|
| Ingestion | Kafka, AWS Kinesis, Pub/Sub |
| Batch processing | Spark, dbt, Airflow |
| Stream processing | Kafka Streams, Flink, Spark Streaming |
| Storage | Data warehouse (BigQuery, Snowflake, Redshift), Data lake (S3 + Parquet) |
| Serving | REST API, GraphQL, materialized views |

### CAP Theorem (Quick Reference)

You can only have 2 of 3:
- **Consistency:** Every read gets the most recent write
- **Availability:** Every request gets a response
- **Partition tolerance:** System works despite network failures

In practice, network partitions happen, so you choose between:
- **CP** (consistency + partition tolerance): System may reject requests during partition. Example: Banking, inventory.
- **AP** (availability + partition tolerance): System always responds, may serve stale data. Example: Social media feeds, like counts.

**Most consumer products lean AP** for read paths (feeds and counts can tolerate slight staleness) with **CP for critical operations** (payments, account changes, inventory).

---

## Quick Study Checklist

### Relational Modeling
- [ ] Given a system, can identify entities and relationships
- [ ] Know when to use a junction table (many-to-many)
- [ ] Can normalize a schema to 3NF and explain why
- [ ] Can denormalize a hot read path and explain the tradeoff
- [ ] Can write the SQL for a denormalized table and explain what it replaces

### Scaling Progression
- [ ] Can explain the 6-step scaling playbook in order (index → replica → cache → denormalize → partition → shard)
- [ ] Know when to use each step (don't shard before you've tried indexing)
- [ ] Can explain indexes: B-tree vs Hash vs GIN and when to use each
- [ ] Can explain read replicas and their consistency tradeoff
- [ ] Can explain cache-aside vs write-through vs TTL

### Sharding & Partitioning
- [ ] Can pick an appropriate shard key and defend the choice
- [ ] Can explain why a bad shard key causes problems (cross-shard queries, hot spots)
- [ ] Know horizontal vs vertical partitioning and when to use each
- [ ] Can explain the full picture: shard → partition → index → cache → replicas

### System-Level
- [ ] Can explain CAP theorem and apply it (feeds/likes = AP, payments/inventory = CP)
- [ ] Understand basic data pipeline (ingest → process → store → serve)
- [ ] Can explain CQRS and when it's appropriate

### Interview Defense Phrases
- "I'd start normalized and denormalize hot paths as needed"
- "I'd shard by X because our access pattern is per-X, so every query hits one shard"
- "I'd partition by date because users mostly access recent data and we can archive old partitions"
- "I'd use PostgreSQL because [relationships/ACID/complex queries], not MongoDB, because [specific reason]"
- "The scaling progression would be: indexes first, then replicas and caching, then denormalize, then partition, then shard - each step handles 10-100x more load"
