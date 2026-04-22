# API Design Principles & SQL vs NoSQL

Two topics that come up constantly in system design interviews: how to design a clean API, and how to defend your database choice.

---

## API Design Principles

### REST Fundamentals

**Use nouns, not verbs:**
```
GOOD: GET /users/123/orders
BAD:  GET /getUserOrders?id=123
```

**HTTP methods map to operations:**
| Method | Purpose | Idempotent? |
|--------|---------|-------------|
| GET | Read resource | Yes |
| POST | Create resource | No |
| PUT | Replace entire resource | Yes |
| PATCH | Partial update | Yes |
| DELETE | Remove resource | Yes |

**Status codes that matter:**
| Code | When |
|------|------|
| 200 | Success (with body) |
| 201 | Created (after POST) |
| 204 | Success (no body, after DELETE) |
| 400 | Bad request (client error, validation) |
| 401 | Unauthorized (not authenticated) |
| 403 | Forbidden (authenticated but no permission) |
| 404 | Not found |
| 409 | Conflict (duplicate, race condition) |
| 429 | Rate limited |
| 500 | Server error |

### Pagination

```
GET /orders?page=2&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 1847,
    "has_next": true
  }
}
```

**Cursor-based (better for real-time data):**
```
GET /orders?cursor=eyJpZCI6MTIzfQ&limit=20
```
- More performant than offset pagination at scale
- No skipped/duplicate results when data changes between pages

### Filtering & Sorting

```
GET /orders?status=pending&customer=42&sort=-date&limit=20
```

### Versioning

```
GET /v1/users/123
# or
Accept: application/vnd.api+json;version=1
```

### API Design Checklist
- [ ] Resources are nouns, not verbs
- [ ] Correct HTTP methods
- [ ] Meaningful status codes
- [ ] Pagination for list endpoints
- [ ] Consistent error response format
- [ ] Rate limiting headers (`X-RateLimit-Remaining`)
- [ ] Idempotency keys for POST (prevent duplicate creates)

---

## SQL vs NoSQL - When to Use Each

### The Decision Framework

**Default to SQL unless you have a specific reason for NoSQL.**

### Use SQL (PostgreSQL, MySQL) When:

| Signal | Why SQL |
|--------|---------|
| Data has relationships | JOINs, foreign keys, referential integrity |
| Need transactions (ACID) | Bank transfers, booking systems, conflict detection |
| Complex queries | Aggregations, GROUP BY, window functions, subqueries |
| Data structure is well-defined | Schema enforces correctness |
| Consistency matters most | Can't afford stale/conflicting reads |

**Examples:** User accounts, orders/payments, calendar events, permissions, inventory

### Use NoSQL When:

**Document Store (MongoDB, DynamoDB):**
| Signal | Why Document |
|--------|-------------|
| Schema varies per record | User profiles with optional fields, product catalogs |
| Read-heavy, denormalized data | Embed related data to avoid JOINs |
| Rapid iteration on schema | Schema-less = easy to change |

**Wide-Column (Cassandra, HBase):**
| Signal | Why Wide-Column |
|--------|-----------------|
| Massive write throughput | Time-series, event logs, counters |
| Data is append-mostly | Logs, analytics, IoT sensor data |
| Horizontal scaling is critical | Multi-datacenter, petabyte scale |

**Key-Value (Redis, DynamoDB):**
| Signal | Why Key-Value |
|--------|---------------|
| Simple lookups by key | Sessions, cache, feature flags |
| Ultra-low latency needed | Sub-millisecond reads |
| Ephemeral data | Caches, rate limit counters |

**Graph (Neo4j):**
| Signal | Why Graph |
|--------|-----------|
| Relationships ARE the data | Social networks, recommendation engines |
| Multi-hop queries | "Friends of friends who like X" |

### Defend Your Decision - Template

> "I'd use **[SQL/NoSQL type]** here because **[primary reason]**.
> Specifically, **[concrete requirement]** maps well to **[specific capability]**.
> I considered **[alternative]** but **[why it's worse for this case]**."

### Example Defenses

**"Design a booking system" → PostgreSQL**
> "I'd use PostgreSQL because bookings have strong relationships - users, venues, availability windows, payments - and we need transactions to prevent double-booking when two users try to reserve the same slot. I considered MongoDB for flexible booking metadata, but the query patterns (search by date range, venue, user) and the ACID requirement make SQL the clear fit."

**"Design an analytics counter" → Cassandra**
> "I'd use Cassandra because we're write-heavy with millions of increments per second, data is append-only, and we need horizontal scaling across regions. SQL could handle moderate scale, but at this write throughput with time-series data, Cassandra's LSM-tree storage is purpose-built for this pattern."

**"Design a session store" → Redis**
> "I'd use Redis because sessions are simple key-value lookups, we need sub-millisecond latency, and sessions are ephemeral - if we lose them, users just re-login. A SQL database would be overkill and slower for this access pattern."

### Common Trap: Don't Use NoSQL Just Because "Scale"

PostgreSQL with proper indexing, partitioning, and read replicas handles far more than most people think. You don't need Cassandra until you're doing millions of writes/sec. Start simple, scale when needed.

### Quick Reference Table

| System | Recommended DB | Why |
|--------|---------------|-----|
| User accounts | SQL | Relationships, ACID, complex queries |
| Orders / payments | SQL | Transactions, referential integrity |
| Media / large files | Object storage (S3) + SQL pointer | Large blobs don't belong in DB |
| Session/auth tokens | Redis | Fast lookups, ephemeral |
| Analytics/counters | Cassandra or Redis | Write-heavy, time-series |
| Search index | Elasticsearch | Full-text search, fuzzy matching |
| Cache layer | Redis | Fast reads, TTL support |
| Activity feed | Cassandra or Redis | Write-heavy, time-ordered |
| Chat messages | Cassandra | Write-heavy, time-ordered, scalable |
| User preferences | Document (MongoDB) or SQL | Flexible schema, or simple SQL JSONB |

