# PostgreSQL & SQL Crash Course for System Design

---

## What It Is
PostgreSQL is an open-source, ACID-compliant relational database. It's the go-to SQL database in system design for structured data, complex queries, and transactional workloads. When you say "SQL database" in an interview, you almost always mean PostgreSQL or MySQL.

## When to Choose SQL Over NoSQL
- Data has clear relationships and structure (users, orders, payments)
- Need ACID transactions (financial systems, inventory, bookings)
- Complex queries with joins, aggregations, subqueries
- Data integrity and consistency are top priority
- Access patterns are varied and not fully known upfront

## ACID Properties
- **Atomicity** – transaction is all-or-nothing
- **Consistency** – DB moves from one valid state to another
- **Isolation** – concurrent transactions don't interfere
- **Durability** – committed data survives crashes (written to disk/WAL)

## Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|---|---|---|---|---|
| **Read Uncommitted** | Possible | Possible | Possible | Fastest |
| **Read Committed** (PG default) | No | Possible | Possible | Fast |
| **Repeatable Read** | No | No | Possible* | Moderate |
| **Serializable** | No | No | No | Slowest |

*PostgreSQL's Repeatable Read actually prevents phantom reads too (uses MVCC snapshots).

## MVCC (Multi-Version Concurrency Control)
- PostgreSQL's concurrency strategy — readers never block writers, writers never block readers
- Each transaction sees a snapshot of data at its start time
- Old row versions kept until vacuumed
- **VACUUM** – reclaims dead tuples from old transactions (autovacuum runs by default, but can need tuning at scale)

## Indexing

### B-Tree (Default)
- Balanced tree structure, O(log n) lookups
- Best for: equality and range queries (`=`, `<`, `>`, `BETWEEN`, `ORDER BY`)
- Created by default on primary keys and unique constraints

### Other Index Types
| Type | Use Case |
|---|---|
| **Hash** | Equality-only lookups (rarely used, B-tree is usually better) |
| **GIN (Generalized Inverted)** | Full-text search, JSONB fields, arrays |
| **GiST (Generalized Search Tree)** | Geospatial, range types, nearest-neighbor |
| **BRIN (Block Range)** | Very large, naturally ordered tables (time-series, logs) |

### Index Concepts to Know
- **Composite index** – multi-column index, follows leftmost prefix rule
- **Covering index** – includes all columns needed, avoids table lookup (index-only scan)
- **Partial index** – index on a subset of rows (`WHERE status = 'active'`)
- **Index bloat** – dead tuples inflate index size; REINDEX to fix
- **Trade-off** – indexes speed up reads but slow down writes (must update index on every insert/update/delete)

## Query Execution & EXPLAIN
- **EXPLAIN ANALYZE** – shows actual execution plan with timing
- Key things to look for:
  - **Seq Scan** – full table scan (bad on large tables, needs index)
  - **Index Scan** – using an index (good)
  - **Index Only Scan** – even better, no table lookup
  - **Nested Loop / Hash Join / Merge Join** – join strategies
  - **Sort** – external sort may indicate missing index
- **Query planner** picks the strategy based on table statistics (run ANALYZE to update stats)

## Scaling PostgreSQL

### Vertical Scaling
- Bigger machine (more RAM, CPU, faster disks)
- Simpler, but has a ceiling
- PostgreSQL can effectively use lots of RAM for shared_buffers and OS page cache

### Read Replicas
- **Streaming replication** – async or synchronous replication to read-only replicas
- Route reads to replicas, writes to primary
- **Replication lag** – async replicas may serve stale data (ms to seconds typically)
- Sync replication eliminates lag but adds write latency

### Connection Pooling
- PostgreSQL forks a process per connection (expensive)
- **PgBouncer** or **pgpool-II** – connection poolers that multiplex many app connections to fewer DB connections
- Essential at scale (thousands of concurrent connections)

### Partitioning
- Split a large table into smaller physical tables
- **Range partitioning** – by date range (most common for time-series)
- **List partitioning** – by discrete values (region, status)
- **Hash partitioning** – even distribution by hash of a column
- Improves query performance (partition pruning) and maintenance (drop old partitions)

### Sharding
- Horizontal partitioning across multiple database instances
- PostgreSQL doesn't natively shard — need application-level sharding or tools like Citus
- Shard by: user_id, tenant_id, geo-region
- **Challenges:** cross-shard joins, distributed transactions, rebalancing
- Consider: do you actually need sharding, or will read replicas + partitioning + caching suffice?

## Key PostgreSQL Features

### JSONB
- Store and query JSON documents within a relational table
- Supports indexing (GIN), dot-notation queries, containment operators
- Gives you document-store flexibility inside SQL
- Use case: flexible metadata, user preferences, semi-structured data

### Full-Text Search
- Built-in `tsvector` + `tsquery` with GIN indexing
- Supports ranking, stemming, multiple languages
- Good enough for many use cases; reach for Elasticsearch when you need fuzzy matching, autocomplete, or massive scale

### CTEs & Window Functions
- **CTEs (WITH clauses)** – readable subqueries, recursive queries (org charts, tree structures)
- **Window functions** – ROW_NUMBER, RANK, LAG/LEAD, running totals without GROUP BY collapse
- Powerful for analytics and reporting queries

### Materialized Views
- Precomputed query results stored as a table
- `REFRESH MATERIALIZED VIEW` to update (not real-time)
- Good for expensive aggregation queries that don't need to be live

### Triggers & Functions
- Execute custom logic on insert/update/delete
- Written in PL/pgSQL (or Python, JavaScript via extensions)
- Use sparingly — can make debugging harder

### LISTEN/NOTIFY
- Lightweight pub/sub built into PostgreSQL
- App can subscribe to channels and get notified on changes
- Not a replacement for Kafka/Redis pub/sub at scale, but useful for simple real-time updates

## Write-Ahead Log (WAL)
- Every change written to WAL before applied to data files
- Ensures durability — on crash, replay WAL to recover
- Also used for: streaming replication, point-in-time recovery (PITR), logical replication
- **WAL archiving** – ship WAL files to S3 for backup/disaster recovery

## Transactions & Locking
- **Row-level locking** – default for updates (fine-grained, high concurrency)
- **Advisory locks** – application-level distributed locks via DB
- **SELECT FOR UPDATE** – lock rows you intend to modify (prevents concurrent modification)
- **Deadlocks** – PostgreSQL detects and aborts one transaction automatically

## PostgreSQL vs MySQL (Quick Comparison)

| Feature | PostgreSQL | MySQL |
|---|---|---|
| **ACID compliance** | Full | Full (with InnoDB) |
| **JSON support** | JSONB (indexed, fast) | JSON (less mature) |
| **Full-text search** | Built-in | Built-in (simpler) |
| **Replication** | Streaming (async/sync) | Binlog-based |
| **Partitioning** | Declarative (native) | Native |
| **Extensions** | Rich ecosystem (PostGIS, pg_trgm, Citus) | Limited |
| **Concurrency** | MVCC | MVCC (InnoDB) |
| **Performance** | Better for complex queries | Better for simple reads at high throughput |
| **Community** | Strong, developer-focused | Strong, widely deployed |

In system design interviews, they're mostly interchangeable. Say "relational database like PostgreSQL" and move on.

## Common System Design Use Cases

| Use Case | Why SQL/PostgreSQL |
|---|---|
| **User accounts & auth** | Structured, relational, ACID transactions |
| **E-commerce (orders, inventory)** | Transactions prevent overselling |
| **Financial systems** | ACID is non-negotiable |
| **Social media (core data)** | Users, posts, follows (with caching layer on top) |
| **Booking systems** | Prevent double-booking with row locking |
| **Multi-tenant SaaS** | Schema per tenant or tenant_id sharding |
| **Analytics (OLAP)** | Window functions, materialized views, CTEs |

## Quick Numbers

| Metric | Value |
|---|---|
| Read latency | 1–10ms (indexed queries) |
| Write latency | 2–20ms (depends on durability settings) |
| Connections (default) | 100 (increase with pooler) |
| Max table size | 32TB |
| Max row size | 1.6TB |
| Max columns per table | 250–1600 (depends on types) |
| Max index size | 32TB |

## What to Say in an Interview

**Choosing SQL:** "The data is highly relational with strong consistency requirements, so I'd use PostgreSQL. We can scale reads with replicas and a caching layer, partition large tables by date, and use connection pooling to handle high concurrency."

**Acknowledging limits:** "If we hit write throughput limits on a single primary, we can shard by user_id using Citus or application-level sharding, though we'd lose easy cross-shard joins."

**Hybrid approach:** "Core transactional data in PostgreSQL for consistency, with Redis caching hot reads and Elasticsearch for full-text search."

---

**Bottom line:** PostgreSQL is your default choice when data is structured, relationships matter, and you need transactions. Pair it with caching (Redis), search (Elasticsearch), and async processing (Kafka) to build a complete system. Know how to scale it: read replicas → connection pooling → partitioning → caching → sharding (last resort).
