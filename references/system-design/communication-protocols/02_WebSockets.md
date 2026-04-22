# WebSockets

**Category:** Tier 1 - Must Know

---

## Definition

**WebSockets** provide full-duplex, bidirectional communication over a single persistent TCP connection.

---

## Core Characteristics

- **Persistent connection**: Stays open for minutes/hours
- **Bidirectional**: Both client and server can send messages anytime
- **Low overhead**: After handshake, only 2-14 bytes per frame
- **Real-time**: Messages delivered instantly
- **Upgrade from HTTP**: Initial handshake uses HTTP, then upgrades

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  WebSocket Flow                             │
└─────────────────────────────────────────────────────────────┘

Phase 1: HTTP Upgrade Handshake (one-time)
──────────────────────────────────────────
Client                                Server
  │                                     │
  │── HTTP GET /chat ──────────────────>│
  │    Upgrade: websocket               │
  │    Connection: Upgrade              │
  │                                     │
  │<─── 101 Switching Protocols ────────│
  │                                     │
  └──────── WebSocket Connection ───────┘
           (Persistent, stays open)


Phase 2: Bidirectional Messages (continuous)
─────────────────────────────────────────────
Client                                Server
  │                                     │
  │<──── {"type": "user_joined"} ───────│  Server pushes
  │                                     │
  │──── {"msg": "Hello!"} ─────────────>│  Client sends
  │                                     │
  │<──── {"msg": "Hi there!"} ──────────│  Server pushes
  │                                     │
  │──── {"msg": "How are you?"} ───────>│  Client sends
  │                                     │
  (Connection remains open until closed by either side)


Multi-Client Chat Example:
──────────────────────────
Client A         Server              Client B
   │                │                   │
   │─ "Hello!" ────>│                   │
   │                │─ "A: Hello!" ────>│  Server broadcasts
   │                │                   │
   │                │<─ "Hi A!" ────────│
   │<─ "B: Hi A!" ──│                   │  Server broadcasts
   │                │                   │
```

---

## Use Cases

### ✅ Perfect For

1. **Chat applications**
   - Real-time messaging (Slack, Discord)
   - Typing indicators
   - Online status

2. **Live dashboards**
   - Stock tickers
   - Analytics dashboards
   - Monitoring systems

3. **Multiplayer games**
   - Real-time game state synchronization
   - Player movements
   - Real-time leaderboards

4. **Collaborative editing**
   - Google Docs, Figma
   - Whiteboards
   - Code editors (VS Code Live Share)

5. **Notifications**
   - Push notifications without polling
   - Live updates (likes, comments)

### ❌ Bad For

1. **Simple CRUD** - REST is simpler, WebSockets overkill
2. **One-time requests** - Connection overhead not worth it
3. **Large file transfers** - HTTP with range requests better
4. **When you need HTTP caching** - WebSockets can't be cached

---

## Real-World Examples

1. **Slack/Discord**: Real-time chat, typing indicators, presence
2. **Trading platforms**: Live stock prices, order book updates
3. **Figma**: Real-time collaborative design
4. **Google Docs**: Multi-user editing with live cursors
5. **Multiplayer.io games**: Game state sync across players

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| True real-time (instant delivery) | More complex than REST |
| Efficient (low overhead after handshake) | Stateful (server tracks connections) |
| Bidirectional (both directions simultaneously) | Harder to scale (need sticky sessions) |
| Server can push (no polling needed) | No HTTP caching |
| Low latency | Load balancers need special config |

---

## Example Code

### Client (JavaScript)

```javascript
// Connect to WebSocket server
const ws = new WebSocket('wss://example.com/chat');

// Connection opened
ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'join', username: 'Alice' }));
};

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  displayMessage(data);
};

// Send message
function sendMessage(text) {
  ws.send(JSON.stringify({ type: 'message', text }));
}

// Handle disconnect
ws.onclose = () => {
  console.log('Disconnected, attempting reconnect...');
  setTimeout(() => reconnect(), 1000);
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Server (Node.js with ws library)

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const clients = new Set();

wss.on('connection', (ws) => {
  console.log('Client connected');
  clients.add(ws);

  // Receive message from client
  ws.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('Received:', message);

    // Broadcast to all clients
    clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(message));
      }
    });
  });

  // Handle disconnect
  ws.on('close', () => {
    console.log('Client disconnected');
    clients.delete(ws);
  });

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to chat server'
  }));
});

console.log('WebSocket server running on ws://localhost:8080');
```

---

## Connection to Your Work

Think about where you've used (or could use) WebSockets in your own projects. Common scenarios:
- **Real-time control commands**: Instant delivery of user actions (play, pause, stop, submit)
- **Device or presence discovery**: Real-time notifications when users or devices connect/disconnect
- **Status updates**: Live status (connected, streaming, online, typing)
- **Session management**: Real-time session state synchronization across clients

**Why WebSockets:**
- These all need **instant delivery** and **server push**
- REST polling would introduce latency and waste bandwidth
- Bidirectional: Client sends commands, server pushes status updates

---

## Common Failure Mode - Real-Time Chat Question

**Question:** "Design a real-time chat application"

**A typical weak answer progression:**
- Suggests REST (wrong - REST is request/response, not real-time)
- Pivots to GraphQL (still not optimal - GraphQL queries are also request/response)
- Eventually lands on WebSockets but can't defend the choice

**A strong answer sounds like:**
> "I'd use WebSockets. Chat requires bidirectional real-time communication - users send messages and the server must instantly push messages from other users to all participants. REST polling would waste bandwidth and introduce latency - if 1000 users poll every second, that's 1000 requests/sec, and messages are delayed by the polling interval. WebSockets maintain a persistent connection, allowing instant message delivery in both directions with minimal overhead after the initial HTTP upgrade handshake."

**The root issue when this goes wrong:**
- You likely already KNOW WebSockets are the answer
- But under pressure, you can't access that knowledge
- You can't explain WHY WebSockets are the right choice
- You can't articulate TRADEOFFS

---

## Interview Tips

### When to Immediately Say "WebSockets"

Recognize these keywords:
- "Real-time" + "bidirectional"
- "Chat" / "Messaging"
- "Live updates" + "users send data"
- "Multiplayer" / "Collaborative"
- "Instant notifications" + "user actions"

### How to Defend WebSockets

**Template:**
1. **State requirement**: "This needs real-time bidirectional communication"
2. **Explain WebSocket advantage**: "WebSockets maintain a persistent connection for instant message delivery"
3. **Contrast with REST**: "REST polling would waste bandwidth (X requests/sec) and introduce latency (Y second delays)"
4. **Mention tradeoffs**: "WebSockets are more complex than REST and require handling reconnections, but the real-time requirement justifies the added complexity"
5. **Connect to experience**: "Similar to a WebSocket implementation I've worked on for [specific feature]"

### Common Follow-Up Questions

**Q: "How do you handle scaling WebSockets?"**
A: "WebSockets are stateful, so you need sticky sessions (route clients to same server) or use Redis pub/sub to share messages across servers. For very high scale, consider dedicated WebSocket servers separate from application servers."

**Q: "What if the connection drops?"**
A: "Implement automatic reconnection with exponential backoff. Track the last received message ID so clients can request missed messages on reconnect. Consider heartbeat/ping-pong to detect dead connections early."

**Q: "WebSockets vs Server-Sent Events?"**
A: "SSE is simpler but unidirectional (server → client only). For chat where clients also send messages frequently, WebSockets are necessary. SSE would work for notifications where clients rarely send data."

---

## Key Technical Details

### Handshake Process

1. Client sends HTTP GET with `Upgrade: websocket` header
2. Server responds with `101 Switching Protocols`
3. Connection upgrades from HTTP to WebSocket protocol
4. Both sides can now send messages anytime

### Frame Format

After handshake, messages are sent in frames:
- **Header**: 2-14 bytes (includes opcode, length, mask)
- **Payload**: Your actual data
- Much more efficient than HTTP (no headers per message!)

### Connection Lifecycle

```
1. Connect (HTTP upgrade)
2. Open (ready to send/receive)
3. Message exchange (bidirectional)
4. Close (either side can initiate)
```

---

**Key Takeaway:** WebSockets are THE solution for real-time bidirectional communication. If you hear "chat", "collaborative", "live updates + user actions", immediately think WebSockets and confidently explain why.
