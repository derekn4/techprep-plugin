# CDN & Rate Limiting Study Guide

## CDN (Content Delivery Network)

### What is a CDN?
A global network of edge servers that cache and serve content from locations geographically closer to users.

### Why Use a CDN?
- **Reduced latency** - Content served from nearby edge server, not origin
- **Lower bandwidth costs** - Origin server handles fewer requests
- **Improved reliability** - Multiple edge servers = redundancy
- **Handle traffic spikes** - Distributed load across edge network

### What to Cache (CDN)
| Good for CDN | NOT for CDN |
|--------------|-------------|
| Images, videos, audio | User-specific API responses |
| CSS, JavaScript, fonts | Real-time data (stock prices, live scores) |
| Static HTML pages | Authentication/session data |
| Downloadable files | Uploads (go TO origin) |
| Thumbnails | Live chat messages |

### Cache Invalidation Strategies

**1. Versioned Filenames (Preferred)**
```
styles.css → styles.abc123.css
bundle.js → bundle.v2.3.1.js
```
- CDN sees new filename = new file
- Old version stays cached until TTL expires (harmless)

**2. Cache-Control Headers**
```http
Cache-Control: max-age=31536000  # 1 year for static assets
Cache-Control: no-cache          # Always revalidate
Cache-Control: no-store          # Never cache
```

**3. CDN Purge/Invalidation**
- Manually tell CDN to drop cached content
- Slower, sometimes costs money
- Use sparingly

### CDN in System Design (YouTube Example)

```
User Request → CDN Edge Server
                    ↓
              Cache HIT? → Return cached video chunk
                    ↓ (miss)
              Origin Server → Fetch, cache, return
```

**Through CDN:**
- Video chunks (HLS/DASH segments)
- Thumbnails
- Static assets

**Direct to Origin:**
- Video uploads
- User data APIs
- Comments, likes
- Authentication

### Signed URLs
For protected content (paid videos, private files):
```
https://cdn.example.com/video/abc123.mp4?token=xyz&expires=1699999999
```
- CDN serves content, but URL expires
- Prevents unauthorized sharing

---

## Rate Limiting

### What is Rate Limiting?
Controlling how many requests a client can make within a time window. Protects servers from overload, abuse, and ensures fair usage.

### Where to Implement
1. **API Gateway** (most common) - Kong, AWS API Gateway, nginx
2. **Load Balancer** - HAProxy, nginx
3. **Application Middleware** - Express middleware, Django middleware
4. **Dedicated Service** - Separate rate limit microservice

### Why Redis for Rate Limiting?
- **In-memory speed** - Sub-millisecond latency
- **Atomic operations** - `INCR`, `EXPIRE` prevent race conditions
- **Built-in TTL** - Keys auto-expire
- **Distributed** - Shared state across app servers

---

## Rate Limiting Algorithms

### 1. Fixed Window

**How it works:** Count requests in fixed time windows (e.g., 0:00-0:59, 1:00-1:59).

**Pros:** Simple, low memory
**Cons:** Burst at window edges (user can do 100 requests at 0:59, then 100 more at 1:00)

```python
# Redis Implementation - Fixed Window
def is_allowed_fixed_window(user_id, limit=100, window_seconds=60):
    # Key includes the current window timestamp
    window = int(time.time() / window_seconds)
    key = f"rate_limit:{user_id}:{window}"

    current = redis.incr(key)

    if current == 1:
        redis.expire(key, window_seconds)

    return current <= limit
```

---

### 2. Sliding Window Log

**How it works:** Store timestamp of each request. Count requests in last N seconds.

**Pros:** Precise, no edge bursts
**Cons:** High memory (stores every timestamp)

```python
# Redis Implementation - Sliding Window Log
def is_allowed_sliding_log(user_id, limit=100, window_seconds=60):
    key = f"rate_limit:{user_id}"
    now = time.time()
    window_start = now - window_seconds

    # Remove old entries, add new one, count
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)  # Remove old
    pipe.zadd(key, {str(now): now})              # Add current
    pipe.zcard(key)                               # Count
    pipe.expire(key, window_seconds)              # TTL
    results = pipe.execute()

    count = results[2]
    return count <= limit
```

---

### 3. Sliding Window Counter

**How it works:** Hybrid of fixed window + weighted previous window. Approximates sliding window with less memory.

**Pros:** Smooth, memory efficient
**Cons:** Approximate (not exact)

```python
# Redis Implementation - Sliding Window Counter
def is_allowed_sliding_counter(user_id, limit=100, window_seconds=60):
    now = time.time()
    current_window = int(now / window_seconds)
    previous_window = current_window - 1

    # How far into current window (0.0 to 1.0)
    position_in_window = (now % window_seconds) / window_seconds

    current_key = f"rate_limit:{user_id}:{current_window}"
    previous_key = f"rate_limit:{user_id}:{previous_window}"

    current_count = int(redis.get(current_key) or 0)
    previous_count = int(redis.get(previous_key) or 0)

    # Weighted sum: full current + partial previous
    weighted_count = current_count + (previous_count * (1 - position_in_window))

    if weighted_count < limit:
        redis.incr(current_key)
        redis.expire(current_key, window_seconds * 2)
        return True

    return False
```

---

### 4. Token Bucket

**How it works:** Bucket holds tokens. Each request takes a token. Tokens refill at steady rate. Allows bursts up to bucket capacity.

**Pros:** Allows controlled bursts, smooth average rate
**Cons:** Slightly more complex

```python
# Redis Implementation - Token Bucket
def is_allowed_token_bucket(user_id, capacity=100, refill_rate=10):
    """
    capacity: max tokens (max burst size)
    refill_rate: tokens added per second
    """
    key = f"token_bucket:{user_id}"
    now = time.time()

    # Get current bucket state
    bucket = redis.hgetall(key)

    if bucket:
        tokens = float(bucket[b'tokens'])
        last_refill = float(bucket[b'last_refill'])

        # Calculate tokens to add since last request
        elapsed = now - last_refill
        tokens = min(capacity, tokens + (elapsed * refill_rate))
    else:
        tokens = capacity
        last_refill = now

    # Try to consume a token
    if tokens >= 1:
        tokens -= 1
        redis.hset(key, mapping={'tokens': tokens, 'last_refill': now})
        redis.expire(key, capacity / refill_rate * 2)  # TTL
        return True

    return False
```

---

### 5. Leaky Bucket

**How it works:** Requests enter a queue (bucket). Processed at constant rate. If bucket full, new requests rejected.

**Pros:** Perfectly smooth output rate
**Cons:** No bursts allowed, requests may wait

```python
# Redis Implementation - Leaky Bucket (using sorted set as queue)
def is_allowed_leaky_bucket(user_id, capacity=100, leak_rate=10):
    """
    capacity: max queue size
    leak_rate: requests processed per second
    """
    key = f"leaky_bucket:{user_id}"
    now = time.time()

    # Calculate how many "leaked" since we need to remove old ones
    # In practice, leaky bucket is often implemented as a queue processor
    # This is a simplified version using token bucket math inverted

    bucket = redis.hgetall(key)

    if bucket:
        water_level = float(bucket[b'level'])
        last_leak = float(bucket[b'last_leak'])

        # Leak water since last request
        elapsed = now - last_leak
        water_level = max(0, water_level - (elapsed * leak_rate))
    else:
        water_level = 0
        last_leak = now

    # Try to add water (request)
    if water_level < capacity:
        water_level += 1
        redis.hset(key, mapping={'level': water_level, 'last_leak': now})
        redis.expire(key, capacity / leak_rate * 2)
        return True

    return False
```

---

## Algorithm Comparison

| Algorithm | Burst Handling | Memory | Precision | Use Case |
|-----------|---------------|--------|-----------|----------|
| Fixed Window | Edge bursts possible | Low | Low | Simple APIs |
| Sliding Log | No bursts | High | Exact | When precision matters |
| Sliding Counter | Smooth | Medium | Approximate | Good balance |
| Token Bucket | Controlled bursts | Low | Good | Most APIs (recommended) |
| Leaky Bucket | No bursts | Low | Good | Smooth output needed |

---

## Quick Reference - Interview Answer

**"How would you implement rate limiting?"**

> "I'd use a Token Bucket algorithm with Redis. Token bucket allows controlled bursts while maintaining an average rate limit.
>
> Implementation: Store tokens and last_refill timestamp in Redis hash. On each request, calculate tokens to add based on elapsed time, try to consume one token. Use Redis for atomic operations and shared state across servers.
>
> I'd put this at the API Gateway layer so it applies to all services consistently. For distributed systems, Redis gives us a single source of truth for rate limit state across all app servers."

---

*Created: January 12, 2026*
