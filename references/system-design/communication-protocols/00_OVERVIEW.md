# Communication Protocols - Overview & Quick Reference

**Purpose:** Quick decision guide for system design interviews.

**Last Updated:** November 24, 2025

---

## Quick Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    Which Protocol to Use?                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   Need real-time updates?
                              │
                 ┌────────────┴────────────┐
                 │                         │
                NO                        YES
                 │                         │
                 ▼                         ▼
     Complex nested queries?      Who initiates communication?
                 │                         │
         ┌───────┴───────┐        ┌────────┴─────────┐
         │               │        │                   │
        YES             NO     Client                 │
         │               │        │                   │
         ▼               ▼        ▼                   ▼
     GraphQL          REST   One-way or        Server-to-Server?
                             bidirectional?             │
                                  │                     │
                         ┌────────┴────────┐           ▼
                         │                 │       Webhooks
                    One-way          Bidirectional
                         │                 │
                         ▼                 ▼
                Server→Client?        WebSockets
                         │              (or gRPC if
                         │             microservices)
                    ┌────┴────┐
                    │         │
               Unidirectional Binary/High-perf?
                    │         │
                    ▼         ▼
                   SSE      gRPC Stream
```

---

## Complete Comparison Table

| Protocol | Direction | Transport | Data Format | Real-Time | Use Case | Complexity |
|----------|-----------|-----------|-------------|-----------|----------|------------|
| **REST** | Client→Server | HTTP/1.1 | JSON | ❌ | CRUD APIs | Low |
| **WebSockets** | Bidirectional | WebSocket | Binary/Text | ✅ | Chat, games | Medium |
| **GraphQL** | Client→Server | HTTP | JSON | ❌ | Complex queries | Medium-High |
| **gRPC** | Bidirectional | HTTP/2 | Protobuf | ✅ | Microservices | High |
| **SSE** | Server→Client | HTTP | Text | ✅ | Notifications | Low |
| **Webhooks** | Server→Server | HTTP | JSON | ❌ | Event callbacks | Low |
| **Long Polling** | Client→Server | HTTP | JSON | ⚠️ | Fallback | Medium |
| **Message Queues** | Async | TCP | Binary | ❌ | Task queues | Medium-High |
| **MQTT** | Pub/Sub | TCP | Binary | ✅ | IoT | Medium |
| **WebRTC** | P2P | UDP/TCP | Binary | ✅ | Video calls | High |

---

## Quick Reference Cheat Sheet

| Scenario | Protocol | Why |
|----------|----------|-----|
| CRUD operations | REST | Simple, standard, cacheable |
| Real-time chat | WebSockets | Bidirectional, instant |
| Live notifications (one-way) | SSE | Simpler than WebSockets |
| Payment callbacks | Webhooks | Event-driven, no polling |
| Complex nested queries | GraphQL | Flexible, reduces round trips |
| Microservices (internal) | gRPC | Fast, strongly typed |
| Mobile bandwidth optimization | GraphQL | No over-fetching |
| IoT sensors | MQTT | Lightweight, low bandwidth |
| Video calls | WebRTC | P2P, low latency |
| Background jobs | Message Queues | Async, reliable |

---

## Interview Priority (What to Master)

### Tier 1: Must Know (90% of interviews)
1. ✅ **REST** - Foundation, everywhere
2. ✅ **WebSockets** - Real-time communication
3. ✅ **GraphQL** - Modern API alternative

### Tier 2: Should Know (Differentiator)
4. ⚠️ **SSE** - Simple real-time
5. ⚠️ **Webhooks** - Server-to-server events
6. ⚠️ **gRPC** - Microservices communication

### Tier 3: Nice to Know (Specialized)
7. Long Polling, Message Queues, MQTT, WebRTC

---

## Key Interview Talking Points

### "Why Not REST for Real-Time?"

> "REST is request-response - the client must initiate every interaction. For real-time features like chat, we'd need to poll constantly, which wastes bandwidth and introduces latency. If we poll every second, that's 1000 requests/second for 1000 users, and messages are delayed up to 1 second. WebSockets maintain a persistent connection where the server can push updates instantly when they happen, with minimal overhead after the initial handshake."

### "GraphQL vs REST?"

> "I'd choose based on client flexibility needs. GraphQL shines when you have multiple clients (iOS, Android, Web) with different data requirements, or when you want to reduce API calls by fetching nested data in one query. However, REST is simpler and has better caching support. For a mobile app with complex data needs, GraphQL reduces over-fetching and round trips. For a simple CRUD API, REST is more straightforward."

### "WebSockets vs SSE?"

> "Both provide real-time server push, but SSE is unidirectional (server to client only) while WebSockets are bidirectional. For notifications or live scores where clients only receive updates, SSE is simpler - it's built on HTTP, has automatic reconnection, and works with standard HTTP infrastructure. For chat or games where clients also send data frequently, WebSockets are necessary. SSE is basically 'WebSockets lite' for when you only need server-to-client communication."

### "When to Use Webhooks?"

> "Webhooks are the 'reverse API' pattern - instead of polling an API asking 'is it done yet?', the service calls you when something happens. This is perfect for third-party integrations like Stripe payments or GitHub events. The key considerations are security (verify webhook signatures), reliability (handle retries and duplicates), and async processing (return 200 quickly, process in background). Webhooks are server-to-server, not for client applications."

---

## Files in This Directory

- `00_OVERVIEW.md` - This file (decision tree, comparison table)
- `01_REST.md` - REST architecture, use cases, examples
- `02_WebSockets.md` - WebSocket protocol, real-time communication
- `03_GraphQL.md` - GraphQL queries, schema, use cases
- `04_SSE.md` - Server-Sent Events, unidirectional streaming
- `05_Webhooks.md` - Webhook pattern, event-driven architecture
- `06_gRPC.md` - gRPC, Protocol Buffers, microservices
- `07_Other_Protocols.md` - Long Polling, Message Queues, MQTT, WebRTC
- `08_Practice_Scenarios.md` - Practice problems with solutions

---

**Remember:** There's rarely one "right" answer in system design. Explain tradeoffs and justify your choice based on requirements.
