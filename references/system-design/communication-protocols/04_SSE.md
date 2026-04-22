# Server-Sent Events (SSE)

**Category:** Tier 2 - Should Know

---

## Definition

**Server-Sent Events (SSE)** is a unidirectional protocol where the server pushes updates to clients over a persistent HTTP connection.

**Think of it as:** "WebSockets, but only server → client, and uses regular HTTP"

---

## Core Characteristics

- **Unidirectional**: Server → Client only
- **HTTP-based**: Built on standard HTTP (not separate protocol)
- **Persistent connection**: Stays open, server sends events
- **Automatic reconnection**: Browser auto-reconnects if dropped
- **Text-based**: Events are text (typically JSON)

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Server-Sent Events (SSE) Flow                  │
└─────────────────────────────────────────────────────────────┘

Client                                    Server
  │                                          │
  │── GET /events ─────────────────────────>│
  │    Accept: text/event-stream            │
  │                                          │
  │                         (Connection stays open)
  │                                          │
  │<───── data: {"score": "3-2"} ───────────│  Server pushes
  │                                          │
  │<───── data: {"score": "4-2"} ───────────│  Server pushes
  │                                          │
  │<───── data: {"status": "game over"} ────│  Server pushes
  │                                          │
  │                          [Connection drops]
  │                                          │
  │── GET /events (auto-reconnect) ────────>│  Browser auto-reconnects
  │                                          │


Real-World Example: Live Scores
────────────────────────────────
┌─────────────┐              ┌──────────────┐
│   Browser   │              │    Server    │
│             │              │              │
│  ┌────────┐ │              │  ┌────────┐  │
│  │Score   │ │<─── SSE ─────│  │Database│  │
│  │Widget  │ │   events     │  │polls   │  │
│  └────────┘ │              │  │sports  │  │
│             │              │  │API     │  │
└─────────────┘              │  └────────┘  │
                             └──────────────┘
      ▲                              │
      │                              │
      └──── Display updates ─────────┘
            as events arrive
```

---

## Use Cases

### ✅ Perfect For

1. **Live notifications** (one-way: server → client)
2. **Stock tickers / live scores** (updates pushed from server)
3. **News feeds** (new articles as published)
4. **Server monitoring** (health status updates)
5. **Live logs** (server logs streamed to dashboard)

### ❌ Bad For

1. **Bidirectional communication** (use WebSockets)
2. **Client needs to send data** (SSE is receive-only)
3. **Binary data** (SSE is text-only)
4. **IE support** (IE doesn't support SSE)

---

## Real-World Examples

1. **Twitter/X**: Live tweet streams
2. **Financial dashboards**: Real-time stock prices
3. **Sports apps**: Live game scores
4. **News sites**: Breaking news alerts
5. **Monitoring tools**: Server health status

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| Simpler than WebSockets | Unidirectional only (server → client) |
| Automatic reconnection | Text-only (no binary) |
| Built on HTTP (works with proxies) | Limited browser support (no IE) |
| Easy to implement | Connection limits (6 per domain in browsers) |
| No special server required | Less efficient than WebSockets for high-frequency |

---

## Example Code

### Client (JavaScript)

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('/events');

// Listen for messages (default event type)
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
  updateUI(data);
};

// Listen for custom event types
eventSource.addEventListener('score', (event) => {
  const score = JSON.parse(event.data);
  updateScore(score);
});

eventSource.addEventListener('status', (event) => {
  const status = JSON.parse(event.data);
  updateStatus(status);
});

// Handle errors
eventSource.onerror = (error) => {
  console.error('Connection error, will auto-reconnect');
  // Browser will automatically reconnect
};

// Close connection (optional)
eventSource.close();
```

### Server (Node.js)

```javascript
const express = require('express');
const app = express();

app.get('/events', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');

  // Send event every 5 seconds
  const intervalId = setInterval(() => {
    const data = {
      time: Date.now(),
      score: '3-2',
      team1: 'Lakers',
      team2: 'Warriors'
    };

    // Default event type
    res.write(`data: ${JSON.stringify(data)}\n\n`);

    // Custom event type
    res.write(`event: score\n`);
    res.write(`data: ${JSON.stringify({ home: 3, away: 2 })}\n\n`);
  }, 5000);

  // Cleanup on disconnect
  req.on('close', () => {
    clearInterval(intervalId);
    res.end();
  });
});

app.listen(3000);
```

---

## SSE vs WebSockets

| Feature | SSE | WebSockets |
|---------|-----|------------|
| **Direction** | Server → Client only | Bidirectional |
| **Protocol** | HTTP | WebSocket protocol |
| **Data format** | Text only | Text or binary |
| **Reconnection** | Automatic | Manual |
| **Browser support** | Good (not IE) | Excellent |
| **Complexity** | Simple | Medium |
| **Use case** | Notifications, updates | Chat, games, collab |

---

## When to Choose SSE over WebSockets

**Use SSE when:**
- ✅ You **only need server → client** (no client → server)
- ✅ Simpler implementation (HTTP-based, auto-reconnect)
- ✅ You want to use HTTP infrastructure (load balancers, proxies work easily)
- ✅ Text data is sufficient (no binary needed)

**Example scenarios:**
- **Live sports scores** - Server pushes score updates, client doesn't need to send anything back
- **Stock ticker** - Server streams price updates
- **Server monitoring dashboard** - Server pushes health metrics
- **News feed** - Server pushes new articles as published

**Use WebSockets when:**
- ❌ Need bidirectional (client sends data frequently)
- ❌ Need binary data
- ❌ Building chat, games, or collaborative tools

---

## Interview Tips

### When to Mention SSE

**Scenario indicators:**
- "Live updates" + "clients don't send data"
- "Notifications"
- "Stock ticker" / "Live scores"
- "Server monitoring"
- "Simpler alternative to WebSockets"

### How to Defend SSE

> "For live stock price updates, SSE is ideal because it's unidirectional - the server pushes price changes, and clients just display them. SSE is simpler than WebSockets since it's built on HTTP, has automatic reconnection, and works with standard HTTP infrastructure. If we later need bidirectional communication (like users placing trades), we can add WebSockets. But for read-only real-time updates, SSE is the simpler choice."

### Common Follow-Ups

**Q: "Why not just use WebSockets for everything?"**
A: "WebSockets are more complex - you have to handle reconnection logic, and they require WebSocket-aware load balancers. For simple server-to-client updates, SSE gives you 80% of the benefit with 20% of the complexity. Use WebSockets when you actually need bidirectional communication."

**Q: "How does SSE handle reconnection?"**
A: "The browser's EventSource API automatically reconnects with exponential backoff. You can also use the `Last-Event-ID` header so the server knows what the client last received and can send missed events."

---

## Advanced Features

### Event IDs (for reconnection)

```javascript
// Server sends event with ID
res.write(`id: 12345\n`);
res.write(`data: ${JSON.stringify(data)}\n\n`);

// On reconnect, client sends last ID
// Server can then send missed events
```

### Custom event types

```javascript
// Server
res.write(`event: notification\n`);
res.write(`data: {"type": "new_message"}\n\n`);

// Client
eventSource.addEventListener('notification', (event) => {
  // Handle notification
});
```

---

## Connection to Your Work

Think about where SSE could fit in systems you've built:
- **Status updates** (if updates are server-initiated only)
- **Notifications** (new items appear server-side)
- **Live feeds / dashboards** (read-only streaming)

**When SSE works well:**
- Client only reads updates
- Any commands the client needs to send can go over a separate REST API

**When WebSockets are better:**
- Need bidirectional communication (send commands + receive updates)
- WebSockets provide both in one connection

---

**Key Takeaway:** SSE is the simple, HTTP-based alternative to WebSockets when you only need server-to-client real-time updates. It's perfect for notifications, live feeds, and monitoring dashboards.
