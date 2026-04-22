# Other Communication Protocols (Tier 3 - Nice to Know)

**Category:** Tier 3 - Specialized/Less Common

These protocols are important for specific use cases but less frequently asked in general system design interviews.

---

## 1. Long Polling

### Definition

**Long Polling** is a technique where the client sends a request, and the server holds it open until data is available or timeout occurs.

### How It Works

```
Short Polling (bad):
────────────────────
Client                  Server
  │                      │
  │── GET /messages ────>│ Empty
  │<─── [] ──────────────│
  ... wait 1 second ...
  │── GET /messages ────>│ Empty
  │<─── [] ──────────────│
  ... wait 1 second ...
  │── GET /messages ────>│ New message!
  │<─── ["Hi"] ──────────│

90% of requests return nothing (wasteful)


Long Polling (better):
───────────────────────
Client                  Server
  │                      │
  │── GET /messages ────>│
  │                      │ Server holds request open
  │                      │ (waits for new data)
  │                      │
  ... 30 seconds later ...
  │                      │ New message arrives!
  │<─── ["Hi"] ──────────│
  │                      │
  │── GET /messages ────>│ Immediately reconnect
  │                      │ (hold open again)
```

### Use Cases
- **Fallback when WebSockets not available** (old browsers, restrictive firewalls)
- **Push notifications** on platforms without WebSocket support

### Pros / Cons
- ✅ Better than short polling (fewer requests)
- ✅ Works with standard HTTP
- ❌ Still not as good as WebSockets
- ❌ Complex to implement correctly (timeouts, reconnection)
- ❌ Each client needs open HTTP connection (server resource usage)

### When to Use
- Legacy browser support required
- WebSockets blocked by firewall/proxy
- Fallback mechanism in progressive enhancement

---

## 2. Message Queues

### Definition

**Message Queues** (RabbitMQ, Apache Kafka, AWS SQS) provide asynchronous communication between services via message passing.

### Architecture

```
┌─────────────────────────────────────────────────┐
│           Message Queue Architecture            │
└─────────────────────────────────────────────────┘

Producer                Queue               Consumer
Service                                     Service
   │                      │                    │
   │── Publish msg ──────>│                    │
   │                   [Queue]                 │
   │                   [msg 1]                 │
   │                   [msg 2]                 │
   │                   [msg 3]                 │
   │                      │                    │
   │                      │<─── Poll ──────────│
   │                      │──── msg 1 ────────>│
   │                      │                    │
   │                      │<─── Ack ───────────│ Processing done
   │                      │                    │
   │                   [msg 2]                 │
   │                   [msg 3]                 │


Use Case: Order Processing
──────────────────────────
┌────────────┐      ┌──────────┐      ┌──────────────┐
│  Web API   │─────>│  Queue   │─────>│   Worker     │
│  (receive  │ put  │ [order1] │ get  │  (process    │
│   orders)  │      │ [order2] │      │   orders)    │
└────────────┘      │ [order3] │      └──────────────┘
                    └──────────┘
                         │
                         └────────────>┌──────────────┐
                                  get  │   Worker 2   │
                                       │  (process    │
                                       │   orders)    │
                                       └──────────────┘
```

### Common Technologies

1. **RabbitMQ**
   - Traditional message broker
   - AMQP protocol
   - Routing, priority queues, dead letter queues

2. **Apache Kafka**
   - High-throughput distributed streaming
   - Log-based architecture
   - Replay messages, partitioning

3. **AWS SQS**
   - Cloud-native, managed
   - Simple, scalable
   - Integrates with AWS services

### Use Cases
- **Decoupling services** (producer doesn't need to know consumer)
- **Handling traffic spikes** (queue absorbs burst, workers process at their pace)
- **Background jobs** (email sending, image processing)
- **Guaranteed delivery** (message persists until acknowledged)
- **Event-driven architecture** (order placed → trigger inventory, shipping, email)

### Pros / Cons
- ✅ Asynchronous (non-blocking)
- ✅ Scalable (add more consumers)
- ✅ Reliable (messages persist)
- ✅ Decoupling (producer/consumer independent)
- ❌ Eventual consistency (not immediate)
- ❌ Complex setup and monitoring
- ❌ Ordering guarantees can be tricky

### When to Use
- Need asynchronous processing
- Handling traffic spikes (queue buffers)
- Building event-driven systems
- Require guaranteed delivery

---

## 3. MQTT (Message Queuing Telemetry Transport)

### Definition

**MQTT** is a lightweight pub/sub protocol designed for IoT devices with limited bandwidth and unreliable networks.

### Architecture

```
┌─────────────────────────────────────────────────┐
│              MQTT Architecture                  │
└─────────────────────────────────────────────────┘

IoT Devices              MQTT Broker         Subscribers
   │                         │                    │
   │                         │                    │
   │── PUBLISH ──────────────>│                   │
   │   topic: "home/temp"    │                   │
   │   payload: 22.5         │                   │
   │                         │                   │
   │                         │─── PUBLISH ──────>│
   │                         │   "home/temp": 22.5│
   │                         │                   │
   │                         │<─── SUBSCRIBE ────│
   │                         │   topic: "home/#" │
   │                         │                   │


Example: Smart Home
───────────────────
Temperature Sensor ─┐
Light Sensor       ─┤
Motion Detector    ─┼──> MQTT Broker ──> Dashboard
Door Sensor        ─┤                  └─> Alert System
Humidity Sensor    ─┘                  └─> Automation
```

### Key Features
- **Quality of Service (QoS)** levels (0, 1, 2)
  - QoS 0: At most once (fire and forget)
  - QoS 1: At least once (acknowledged)
  - QoS 2: Exactly once (guaranteed)
- **Last Will and Testament** (LWT) - Auto-notify if device disconnects
- **Retained messages** - New subscribers get last message immediately
- **Topic hierarchy** - `home/living-room/temperature`

### Use Cases
- **IoT sensors** (temperature, humidity, motion)
- **Smart home automation**
- **Industrial monitoring** (factory sensors)
- **Vehicle telematics** (location, diagnostics)

### Pros / Cons
- ✅ Lightweight (minimal bandwidth)
- ✅ Designed for unreliable networks
- ✅ Pub/sub pattern (decoupled)
- ✅ Low power consumption
- ❌ Not for general web apps
- ❌ Requires MQTT broker
- ❌ Limited browser support

### When to Use
- Building IoT systems
- Devices with limited bandwidth
- Unreliable network connections
- Battery-powered devices

---

## 4. WebRTC (Web Real-Time Communication)

### Definition

**WebRTC** enables peer-to-peer real-time communication (video, audio, data) directly between browsers without a server middleman.

### Architecture

```
┌─────────────────────────────────────────────────┐
│            WebRTC P2P Connection                │
└─────────────────────────────────────────────────┘

Phase 1: Signaling (uses WebSockets or other)
──────────────────────────────────────────────
Browser A          Signaling Server        Browser B
    │                     │                     │
    │── Offer ───────────>│                     │
    │   (SDP)             │──── Offer ─────────>│
    │                     │     (SDP)           │
    │                     │                     │
    │                     │<─── Answer ─────────│
    │<─── Answer ─────────│     (SDP)           │
    │     (SDP)           │                     │
    │                     │                     │
    │── ICE Candidates ──>│                     │
    │                     │──── ICE ───────────>│
    │                     │                     │

Phase 2: Direct P2P Connection
───────────────────────────────
Browser A                              Browser B
    │                                      │
    └──────── Direct P2P Connection ──────┘
         (Video, Audio, Data)
         (No server in the middle!)


NAT Traversal (STUN/TURN):
───────────────────────────
┌─────────┐              ┌─────────┐
│Browser A│              │Browser B│
└────┬────┘              └────┬────┘
     │                        │
     │   ┌──────────────┐     │
     ├───┤ STUN Server  │─────┤  (Discovers public IP)
     │   └──────────────┘     │
     │                        │
     │   ┌──────────────┐     │
     └───┤ TURN Server  │─────┘  (Relay if P2P fails)
         └──────────────┘
```

### Key Components
- **Signaling**: Exchange connection info (uses WebSockets, not WebRTC)
- **STUN**: Discover public IP address
- **TURN**: Relay server when P2P impossible (firewall/NAT)
- **ICE**: Framework for NAT traversal
- **SDP**: Session Description Protocol (media capabilities)

### Use Cases
- **Video conferencing** (Zoom, Google Meet, Discord)
- **Screen sharing**
- **P2P file transfer** (no upload to server)
- **Live streaming** (broadcaster to viewers)
- **Real-time gaming** (P2P multiplayer)

### Pros / Cons
- ✅ P2P (no server bandwidth)
- ✅ Low latency (direct connection)
- ✅ Native browser support
- ✅ Encrypted by default
- ❌ Complex NAT traversal
- ❌ Requires signaling server
- ❌ Difficult to scale (mesh vs SFU)

### When to Use
- Video/audio calls needed
- Low latency critical (P2P advantage)
- Want to save server bandwidth
- Browser-to-browser communication

---

## Quick Comparison

| Protocol | Best For | Avoid For |
|----------|----------|-----------|
| **Long Polling** | Fallback for old browsers | Primary solution (use WebSockets) |
| **Message Queues** | Async jobs, event-driven | Real-time client communication |
| **MQTT** | IoT, sensor data | General web applications |
| **WebRTC** | Video calls, P2P data | Simple request-response |

---

## Interview Context

These protocols rarely come up in general system design interviews, but:

**Long Polling:**
- Mention as fallback for WebSockets
- "For real-time notifications, I'd use WebSockets with long polling as fallback for older browsers"

**Message Queues:**
- Common in microservices discussions
- "To handle traffic spikes, I'd use a message queue between API and workers"
- "For event-driven architecture, Kafka or RabbitMQ for inter-service communication"

**MQTT:**
- Only if specifically IoT domain
- "For IoT sensor data, MQTT's lightweight protocol is ideal for constrained devices"

**WebRTC:**
- Only if video/audio mentioned
- "For video calls, WebRTC provides P2P with low latency, but requires signaling server for connection setup"

---

**Key Takeaway:** These are specialized protocols. Know they exist and what problems they solve, but don't need deep expertise unless your domain specifically requires them (IoT → MQTT, video calls → WebRTC, async processing → Message Queues).
