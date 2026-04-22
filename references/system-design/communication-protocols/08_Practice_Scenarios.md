# Practice Scenarios with Solutions

**Purpose:** Test your understanding of which protocol to use and why.

---

## How to Use This File

1. Read the scenario
2. Choose a protocol (REST / WebSockets / GraphQL / SSE / Webhooks / gRPC / Other)
3. Think about WHY that protocol
4. Consider tradeoffs and alternatives
5. Then read the solution

---

## Scenario 1: Real-Time Chat Application

### Requirements
- Users send/receive messages instantly
- Typing indicators
- Online status
- Message history (load on demand)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: WebSockets + REST (Hybrid)**

**Primary: WebSockets**
- Real-time bidirectional messaging
- Typing indicators and presence require server push
- Low latency for instant message delivery

**Secondary: REST**
- Load message history: `GET /messages?before=timestamp`
- User profile updates: `PUT /users/{id}`
- One-time operations don't need WebSocket

**Why NOT GraphQL alone:**
- GraphQL is request-response, not real-time
- Would need GraphQL Subscriptions (which use WebSockets under the hood)

**Why NOT SSE:**
- Need bidirectional (users send messages frequently)
- SSE only server → client

**Architecture:**
```
Client ─── WebSocket ───> Chat Server (real-time messages)
Client ─── REST API  ───> Chat Server (history, profiles)
```

**Interview Answer:**
> "I'd use WebSockets for real-time messaging, typing indicators, and presence. WebSockets provide bidirectional communication with low latency, perfect for instant message delivery. For loading message history and updating profiles, I'd use REST - these are one-time operations that don't need a persistent connection. This hybrid approach uses the right tool for each requirement."

</details>

---

## Scenario 2: E-Commerce Product Catalog

### Requirements
- Browse products (10,000+ products)
- Filter by category
- Search by name
- Product details with reviews
- Mobile app + web app (different data needs)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: REST (or GraphQL for mobile optimization)**

**Option 1: REST (Simpler)**
```
GET /products?category=electronics&page=1
GET /products/{id}
GET /products/{id}/reviews
```

**Pros:**
- Simple, standard, widely understood
- Cacheable (product data doesn't change often)
- Easy to implement and debug

**Cons:**
- Multiple requests for product + reviews
- Over-fetching (get all fields when client needs few)

**Option 2: GraphQL (Mobile Optimization)**
```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
    name
    price
    images(limit: 3)  # Mobile: Only 3 images
    reviews(limit: 5) {
      text
      rating
    }
  }
}
```

**Pros:**
- Single request for product + reviews
- Mobile app requests only needed fields (saves bandwidth)
- Web app can request more data without backend changes

**Cons:**
- More complex than REST
- No HTTP caching

**Why NOT WebSockets:**
- No real-time requirement
- Product catalog doesn't change every second

**Decision Factors:**
- **Simple e-commerce with minimal mobile optimization needs** → REST
- **Mobile-first, complex nested data, multiple clients** → GraphQL

**Interview Answer:**
> "For the product catalog, I'd start with REST. It's simple, cacheable, and handles CRUD operations well. If mobile bandwidth becomes a concern or we need to reduce API calls, I'd consider GraphQL to let clients specify exactly what fields they need. For example, mobile might request only 3 product images while web requests 10, all without backend changes. But unless we have those specific optimization needs, REST is the pragmatic choice."

</details>

---

## Scenario 3: Payment Processing (Stripe Integration)

### Requirements
- Your service processes orders
- Stripe handles payments
- Need to know when payment succeeds/fails
- Update order status in your database
- Send confirmation email to customer

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: Webhooks**

**How it works:**
1. User submits payment on your site
2. Your server calls Stripe API to initiate payment
3. **Stripe processes payment asynchronously**
4. **Stripe sends webhook to your server** when payment completes
5. Your server updates database and sends email

**Why Webhooks:**
- Payment processing is asynchronous (takes seconds)
- Polling Stripe API is wasteful and has rate limits
- Stripe pushes notification when payment completes (efficient)

**Why NOT REST polling:**
```
// BAD: Polling (wasteful)
while (!paymentComplete) {
  status = stripe.checkPayment(paymentId);
  sleep(1000);
}
```
- Wastes API calls
- Delays notification
- Rate limit issues

**Why NOT WebSockets:**
- Server-to-server (not client-facing)
- Event-driven notification pattern

**Implementation:**
```javascript
// Register webhook
stripe.webhooks.register({
  url: 'https://yoursite.com/stripe-webhook',
  events: ['payment_intent.succeeded', 'payment_intent.failed']
});

// Handle webhook
app.post('/stripe-webhook', (req, res) => {
  // Verify signature
  const event = verifyWebhook(req);

  if (event.type === 'payment_intent.succeeded') {
    updateOrder(event.data.object.metadata.order_id, 'paid');
    sendEmail(event.data.object.receipt_email, 'Payment confirmed');
  }

  res.sendStatus(200); // Acknowledge immediately
});
```

**Interview Answer:**
> "I'd use webhooks for Stripe payment notifications. Instead of polling Stripe asking 'is the payment done yet?', Stripe calls our webhook endpoint when the payment completes. This is efficient (no wasted API calls), provides instant notification, and is the standard pattern for payment integrations. The key considerations are security (verify webhook signatures), reliability (handle retries), and idempotency (use event IDs to avoid processing duplicates)."

</details>

---

## Scenario 4: Live Sports Scoreboard

### Requirements
- Display scores for 10 games
- Updates every 2 seconds
- 100,000 concurrent users watching
- Users don't send any data (read-only)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: SSE (or WebSockets)**

**Preferred: Server-Sent Events (SSE)**

**Why SSE:**
- Unidirectional (server → client only)
- Users don't need to send data
- Simpler than WebSockets (HTTP-based, auto-reconnect)
- Works with standard HTTP infrastructure

```javascript
// Client
const eventSource = new EventSource('/live-scores');
eventSource.onmessage = (event) => {
  const scores = JSON.parse(event.data);
  updateScoreboard(scores);
};
```

**Why NOT REST polling:**
```
// BAD: Polling (100k users × 0.5 req/sec = 50k req/sec!)
setInterval(() => {
  fetch('/scores').then(updateScoreboard);
}, 2000);
```
- 100,000 users × 0.5 requests/sec = 50,000 requests/sec
- Massive server load
- Delayed updates (up to 2 seconds)

**Alternative: WebSockets**
- Also works well
- Slightly more complex (need to handle reconnection)
- Overkill if users never send data

**Scaling Considerations:**
```
┌──────────┐         ┌──────────────┐
│ Sports   │────────>│ Redis Pub/Sub│
│ API      │         │              │
└──────────┘         └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │ SSE     │   │ SSE     │   │ SSE     │
         │ Server 1│   │ Server 2│   │ Server 3│
         └─────────┘   └─────────┘   └─────────┘
              │             │             │
          (33k users)   (33k users)   (33k users)
```

**Interview Answer:**
> "I'd use Server-Sent Events (SSE). The scoreboard is read-only - users receive updates but don't send data. SSE is perfect for this: it's unidirectional (server → client), built on HTTP so it works with existing infrastructure, and has automatic reconnection. For 100k concurrent users, I'd scale horizontally with multiple SSE servers, using Redis Pub/Sub to broadcast score updates from the sports data API to all servers. If we later need bidirectional communication (like live betting), we can upgrade to WebSockets."

</details>

---

## Scenario 5: Microservices Architecture (15 services)

### Requirements
- Service-to-service communication
- High performance critical (financial system)
- Multiple languages (Go, Python, Java, C++)
- Need strong contracts (prevent version mismatches)
- Internal only (no browser clients)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: gRPC (internal) + REST (external)**

**Internal: gRPC**

**Why gRPC:**
- Very fast (binary Protocol Buffers, HTTP/2)
- Strongly typed (.proto files prevent version mismatches)
- Code generation in all languages (Go, Python, Java, C++)
- Multiple patterns (unary, streaming)

**Architecture:**
```
┌─────────────┐         ┌─────────────┐
│   Order     │◄─gRPC──►│  Payment    │
│  Service    │         │  Service    │
│  (Go)       │         │  (C++)      │
└──────┬──────┘         └─────────────┘
       │
       │ gRPC
       │
       ▼
┌─────────────┐         ┌─────────────┐
│  Inventory  │◄─gRPC──►│  Shipping   │
│  Service    │         │  Service    │
│  (Python)   │         │  (Java)     │
└─────────────┘         └─────────────┘
```

**External: REST**
```
Mobile App ─── REST ───> API Gateway ─── gRPC ───> Services
```

**Why NOT REST internally:**
- Slower (JSON parsing, larger payloads)
- Weaker contracts (runtime validation only)
- Higher latency (matters for financial system)

**Why NOT GraphQL:**
- gRPC better for service-to-service
- GraphQL for flexible client queries, not ideal for high-perf backend

**Proto Contract Example:**
```protobuf
service PaymentService {
  rpc ProcessPayment(PaymentRequest) returns (PaymentResponse);
  rpc GetPaymentStatus(StatusRequest) returns (StatusResponse);
}
```

**Interview Answer:**
> "For internal microservices in a financial system, I'd use gRPC. It provides significant performance benefits - Protocol Buffers are binary (30% smaller than JSON) and HTTP/2 multiplexing reduces latency. Strong typing via .proto files catches errors at compile time, preventing version mismatches between services. Code generation works in all languages (Go, Python, Java, C++), making it easy to add services. For external APIs facing mobile apps, I'd use REST at the API Gateway level - it's more accessible. But for internal service-to-service where performance is critical, gRPC is the right choice."

</details>

---

## Scenario 6: Social Media Feed (Mobile App)

### Requirements
- Display feed (posts + comments + likes + author info)
- Different screens need different data
  - Feed screen: Posts + first 3 comments + like count
  - Detail screen: Full post + all comments + author profile
- Minimize mobile bandwidth (users on cellular)
- iOS and Android apps

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: GraphQL**

**Why GraphQL:**
- Clients specify exact data needed (reduces bandwidth)
- Single request for nested data (posts + comments + authors)
- Different screens query differently without backend changes

**REST Approach (inefficient):**
```
// Feed screen - 3 requests per post!
GET /posts → [{ id: 1, author_id: 5 }, ...]
GET /users/5 → { name, avatar }
GET /posts/1/comments?limit=3 → [...]

10 posts × 3 requests = 30 requests just to load feed!
```

**GraphQL Approach (efficient):**
```graphql
# Feed screen - 1 request
query FeedScreen {
  feed(limit: 10) {
    id
    content
    likeCount
    author {
      name
      avatar
    }
    comments(limit: 3) {
      text
    }
  }
}

# Detail screen - 1 request with different fields
query DetailScreen($postId: ID!) {
  post(id: $postId) {
    id
    content
    createdAt
    likeCount
    author {
      name
      avatar
      bio
      followerCount
    }
    comments {
      text
      author {
        name
      }
      createdAt
    }
  }
}
```

**Benefits:**
- Feed screen: Only 3 comments, no author bios (saves bandwidth)
- Detail screen: All comments, full author info
- Backend unchanged for different client needs

**Real-Time Updates:**
- Use GraphQL Subscriptions (WebSockets under the hood)
- Or: GraphQL for loading + WebSockets for live updates

**Interview Answer:**
> "For a mobile social media feed, I'd use GraphQL. Mobile bandwidth is expensive, and GraphQL eliminates over-fetching. Instead of making 30 REST requests to load a feed (posts + authors + comments), the mobile client makes one GraphQL query specifying exactly what it needs. The feed screen requests only 3 comments per post, while the detail screen requests all comments - no backend changes needed. This saves significant bandwidth for cellular users. For real-time updates (new likes, comments), I'd add GraphQL Subscriptions or a separate WebSocket connection."

</details>

---

## Scenario 7: IoT Temperature Sensors (10,000 devices)

### Requirements
- Devices send temperature readings every 10 seconds
- Low bandwidth (cellular connections)
- Unreliable networks (sensors in remote locations)
- Multiple subscribers (dashboard, alerts, data lake)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: MQTT**

**Why MQTT:**
- Designed for IoT (lightweight, low bandwidth)
- Handles unreliable networks (QoS levels, reconnection)
- Pub/sub pattern (multiple subscribers)
- Low power consumption (important for battery devices)

**Architecture:**
```
Temperature Sensors          MQTT Broker          Subscribers
      (10,000)
         │                       │                      │
         │── PUBLISH ────────────>│                     │
         │   topic: device/123/temp                    │
         │   payload: 22.5       │                     │
         │                       │                     │
         │                       │─── Forward ────────>│ Dashboard
         │                       │                     │
         │                       │─── Forward ────────>│ Alert System
         │                       │                     │
         │                       │─── Forward ────────>│ Data Lake
```

**MQTT Topics:**
```
device/{device_id}/temperature
device/{device_id}/humidity
device/{device_id}/battery
```

**QoS Levels:**
- QoS 0: Fire and forget (for non-critical readings)
- QoS 1: At least once delivery (for important data)
- QoS 2: Exactly once (for critical commands)

**Why NOT REST:**
```
// BAD: REST polling from 10,000 devices
POST /readings
```
- Too much overhead (HTTP headers)
- High bandwidth usage
- Not designed for constrained devices

**Why NOT WebSockets:**
- MQTT more lightweight
- Better for unreliable networks
- Standard protocol for IoT

**Interview Answer:**
> "For 10,000 IoT temperature sensors, I'd use MQTT. It's specifically designed for constrained devices with limited bandwidth and unreliable networks. MQTT's publish-subscribe pattern allows multiple subscribers (dashboard, alerts, data lake) without devices knowing who's listening. QoS levels ensure reliable delivery even on spotty cellular connections. For critical sensor data, I'd use QoS 1 (at least once delivery). MQTT's small message overhead and low power consumption are crucial for battery-powered remote sensors."

</details>

---

## Scenario 8: Video Call Application

### Requirements
- 1-on-1 video calls
- Low latency critical (< 150ms)
- High-quality audio/video
- Browser-based (no downloads)
- Screen sharing capability

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: WebRTC + WebSockets (Hybrid)**

**Primary: WebRTC (for video/audio)**

**Why WebRTC:**
- Peer-to-peer (direct connection between browsers)
- Very low latency (no server middleman)
- Native browser support
- Encrypted by default (SRTP)
- Handles video, audio, and data channels

**Secondary: WebSockets (for signaling)**

**Why WebSockets for signaling:**
- Need to exchange connection info (SDP, ICE candidates)
- WebRTC doesn't handle signaling itself
- WebSockets perfect for real-time signaling

**Architecture:**
```
Phase 1: Signaling (WebSockets)
────────────────────────────────
Browser A          Signaling Server      Browser B
   │                     │                   │
   │── Offer (SDP) ─────>│                   │
   │                     │─── Offer ────────>│
   │                     │                   │
   │                     │<─── Answer ───────│
   │<─── Answer ─────────│                   │
   │                     │                   │
   │── ICE Candidates ──>│                   │
   │                     │─── ICE ──────────>│
   │                     │                   │

Phase 2: Direct P2P (WebRTC)
─────────────────────────────
Browser A                          Browser B
   │                                  │
   └────── Direct Video/Audio ───────┘
           (No server!)
```

**Additional Components:**
- **STUN server**: Discover public IP (NAT traversal)
- **TURN server**: Relay if P2P impossible (backup)

**Why NOT WebSockets alone:**
```
// BAD: Streaming video through server
Browser A ─── Video ───> Server ─── Video ───> Browser B
```
- Huge server bandwidth cost
- Higher latency (server in the middle)
- Doesn't scale (100 calls = 100× server bandwidth)

**Why NOT REST:**
- Not designed for real-time media
- Way too high latency

**Interview Answer:**
> "For a video call application, I'd use WebRTC for the video/audio streams and WebSockets for signaling. WebRTC establishes a peer-to-peer connection directly between browsers, providing very low latency (< 150ms) and eliminating server bandwidth costs - the server doesn't relay the video. WebSockets handle the initial signaling to exchange connection information. I'd also deploy STUN servers for NAT traversal and TURN servers as a fallback relay when P2P isn't possible due to restrictive firewalls. This architecture scales well - adding users doesn't increase video bandwidth on our servers."

</details>

---

## Scenario 9: CI/CD Pipeline Notifications

### Requirements
- GitHub notifies your CI system when code is pushed
- Run tests automatically
- Deploy if tests pass
- Need reliable delivery (can't miss pushes)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: Webhooks**

**How it works:**
```
Developer          GitHub            Your CI System
    │                │                     │
    │── git push ───>│                     │
    │                │                     │
    │           [Code received]            │
    │                │                     │
    │                │── Webhook POST ────>│
    │                │   { repo, branch,   │
    │                │     commit, ... }   │
    │                │                     │
    │                │<─── 200 OK ─────────│
    │                │                     │
    │                │              [Run tests]
    │                │                     │
    │                │              [Deploy if pass]
```

**Why Webhooks:**
- Event-driven (instant notification when push happens)
- Reliable (GitHub retries if your server is down)
- Standard pattern for CI/CD
- No polling needed

**GitHub Webhook Configuration:**
```javascript
// Register webhook
{
  "url": "https://ci.yourcompany.com/github-webhook",
  "events": ["push", "pull_request", "release"],
  "active": true
}
```

**Your CI Webhook Handler:**
```javascript
app.post('/github-webhook', async (req, res) => {
  // Verify GitHub signature
  const signature = req.headers['x-hub-signature-256'];
  if (!verifyGitHubSignature(req.body, signature)) {
    return res.status(401).send('Invalid signature');
  }

  const event = req.body;

  // Queue CI job
  await ciQueue.add('run-tests', {
    repo: event.repository.full_name,
    branch: event.ref,
    commit: event.after
  });

  // Return 200 immediately
  res.sendStatus(200);
});
```

**Why NOT polling:**
```
// BAD: Polling GitHub
setInterval(async () => {
  const latestCommit = await github.getLatestCommit(repo);
  if (latestCommit !== lastChecked) {
    runTests(latestCommit);
    lastChecked = latestCommit;
  }
}, 30000); // Check every 30 seconds
```
- Delayed (up to 30 sec)
- API rate limits
- Wasteful (checking when nothing changes)

**Why NOT WebSockets:**
- Server-to-server (not client)
- Event-driven notification pattern better

**Interview Answer:**
> "I'd use GitHub webhooks to trigger CI/CD pipelines. When code is pushed, GitHub sends a webhook POST request to our CI system with commit details. This is instant (no polling delay), reliable (GitHub retries failed webhooks), and efficient (no wasted API calls). Our webhook handler verifies the GitHub signature for security, queues the CI job, and returns 200 immediately. GitHub's webhook retry logic ensures we don't miss pushes even if our server is briefly down."

</details>

---

## Scenario 10: Admin Dashboard (Not Time-Critical)

### Requirements
- Server metrics (CPU, memory, disk, network)
- Updates every 30 seconds
- 10 admin users max
- Not mission-critical latency (30-60 sec delay OK)

### Your Answer

_(Think before expanding)_

<details>
<summary>Click for solution</summary>

**Answer: SSE (or even REST polling)**

**Option 1: Server-Sent Events (Recommended)**

**Why SSE:**
- Simple server → client updates
- Auto-reconnection built-in
- Efficient for 30-second updates
- HTTP-based (works with existing infrastructure)

```javascript
// Server
app.get('/metrics', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');

  const interval = setInterval(() => {
    const metrics = getServerMetrics();
    res.write(`data: ${JSON.stringify(metrics)}\n\n`);
  }, 30000); // Every 30 seconds

  req.on('close', () => clearInterval(interval));
});

// Client
const eventSource = new EventSource('/metrics');
eventSource.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  updateDashboard(metrics);
};
```

**Option 2: REST Polling (Also Acceptable)**

**Why REST polling is OK here:**
- Only 10 users (low load)
- 30-second updates (not frequent)
- Simpler implementation

```javascript
// Client
setInterval(async () => {
  const metrics = await fetch('/metrics').then(r => r.json());
  updateDashboard(metrics);
}, 30000);
```

**Why NOT WebSockets:**
- Overkill for 30-second updates
- More complex than needed
- SSE or REST sufficient

**Why NOT gRPC:**
- Browser clients (not service-to-service)
- Not high-performance requirement

**Scaling Consideration:**
If dashboard grows to 1000+ users, then:
- SSE becomes more important (reduce polling requests)
- Or: GraphQL for flexible metric queries

**Interview Answer:**
> "For an admin dashboard with 30-second updates and only 10 users, I'd use Server-Sent Events. It's simpler than WebSockets - HTTP-based with automatic reconnection - but still provides server push for efficiency. The server sends metric updates every 30 seconds, and the browser displays them. With only 10 users, even REST polling would be acceptable (10 users × 2 req/min = 20 req/min, which is negligible). But SSE is slightly more elegant and scales better if we add more admins later. If we needed real-time alerts or bidirectional communication, I'd upgrade to WebSockets."

</details>

---

## Quick Practice (No Solutions)

Test yourself! Choose the protocol for these scenarios:

1. **Uber-like ride tracking** - Users see driver's location update every 2 seconds on map
2. **E-commerce order history** - Users view past orders, filter by date, search
3. **Multiplayer fast-paced game** - 10 players, sync positions 60 times per second
4. **Stock trading platform** - Place orders + receive live price updates
5. **Email marketing service** - Track when emails are delivered/opened/clicked

---

**Answers (brief):**
1. **WebSockets** - Real-time location updates, bidirectional
2. **REST** - Simple CRUD, no real-time needed
3. **WebSockets or WebRTC** - Very high frequency, bidirectional
4. **WebSockets** - Bidirectional (place orders + receive prices)
5. **Webhooks** - Email service notifies you of events

---

**Remember:** The "best" answer depends on specific requirements. Always explain your reasoning and consider tradeoffs!
