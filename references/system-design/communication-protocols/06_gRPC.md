# gRPC

**Category:** Tier 2 - Should Know (Important for Microservices)

---

## Definition

**gRPC** is a high-performance RPC (Remote Procedure Call) framework using HTTP/2 and Protocol Buffers for efficient service-to-service communication.

**Created by:** Google (hence the "g" in gRPC)

---

## Core Characteristics

- **HTTP/2 based**: Multiplexing, header compression, persistent connections
- **Protocol Buffers**: Binary serialization (smaller, faster than JSON)
- **Strongly typed**: Define service contracts with `.proto` files
- **Four patterns**: Unary, server streaming, client streaming, bidirectional
- **Code generation**: Auto-generate client/server code in many languages

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      gRPC Flow                              │
└─────────────────────────────────────────────────────────────┘

1. Unary RPC (like REST, but faster):
────────────────────────────────────
Client                              Server
  │                                    │
  │── GetUser(id: 123) ───────────────>│ (binary Protocol Buffers)
  │                              ┌──────────┐
  │                              │Database  │
  │                              └──────────┘
  │<─── User{name: "Alice"} ────────────────│ (binary)
  │                                    │


2. Server Streaming (server pushes multiple responses):
────────────────────────────────────────────────────────
Client                              Server
  │                                    │
  │── StreamPrices(symbols) ──────────>│
  │                                    │
  │<─── Price{AAPL: 150} ──────────────│
  │<─── Price{AAPL: 151} ──────────────│
  │<─── Price{AAPL: 149} ──────────────│
  │<─── ... (continuous stream)        │


3. Client Streaming (client sends multiple requests):
──────────────────────────────────────────────────────
Client                              Server
  │                                    │
  │── UploadFile(chunk1) ─────────────>│
  │── UploadFile(chunk2) ─────────────>│
  │── UploadFile(chunk3) ─────────────>│
  │                              ┌──────────┐
  │                              │Save file │
  │                              └──────────┘
  │<─── UploadResult{success} ──────────────│


4. Bidirectional Streaming:
────────────────────────────
Client                              Server
  │                                    │
  │── Message("Hello") ────────────────>│
  │<─── Message("Hi!") ─────────────────│
  │── Message("How are you?") ─────────>│
  │<─── Message("Good, you?") ──────────│
  │── Message("Great!") ────────────────>│
  │                                    │


Microservices Architecture with gRPC:
──────────────────────────────────────
┌─────────────┐           ┌─────────────┐
│   API       │           │   User      │
│   Gateway   │◄─ gRPC ──►│   Service   │
│  (Go)       │           │  (Python)   │
└──────┬──────┘           └─────────────┘
       │                          │
       │                          │ gRPC
       │                          ▼
       │                  ┌─────────────┐
       │                  │   Auth      │
       │                  │   Service   │
       │                  │  (Java)     │
       │                  └─────────────┘
       │ gRPC
       ▼
┌─────────────┐           ┌─────────────┐
│   Order     │◄─ gRPC ──►│  Payment    │
│   Service   │           │  Service    │
│  (Node.js)  │           │  (C++)      │
└─────────────┘           └─────────────┘

All services share .proto contract files
```

---

## Use Cases

### ✅ Perfect For

1. **Microservices communication** (internal service-to-service)
2. **High-performance APIs** (trading, financial systems)
3. **Polyglot environments** (services in different languages)
4. **Streaming data** (logs, metrics, sensor data)
5. **Real-time bidirectional** (chat backends, game servers)

### ❌ Bad For

1. **Browser clients** (limited support, need gRPC-Web proxy)
2. **Public APIs** (REST more accessible)
3. **Simple CRUD** (REST simpler, more standard)
4. **Debugging ease** (binary format harder to inspect)

---

## Real-World Examples

1. **Google**: Internal microservices (created gRPC)
2. **Netflix**: Service mesh communication
3. **Uber**: Microservices coordination
4. **Square**: Payment processing services
5. **Dropbox**: File sync services

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| Very fast (binary, HTTP/2) | Complex setup |
| Strongly typed (compile-time safety) | Limited browser support |
| Code generation (less boilerplate) | Not human-readable (binary) |
| Multiple patterns (unary, streaming) | Harder to debug |
| Polyglot (many languages) | Steeper learning curve |

---

## Protocol Buffer Example

### .proto Definition

```protobuf
syntax = "proto3";

package user;

// Service definition
service UserService {
  // Unary RPC
  rpc GetUser(UserRequest) returns (UserResponse);

  // Server streaming
  rpc StreamUsers(StreamRequest) returns (stream UserResponse);

  // Client streaming
  rpc CreateUsers(stream UserRequest) returns (BatchResponse);

  // Bidirectional streaming
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

// Message types
message UserRequest {
  int32 user_id = 1;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message StreamRequest {
  int32 limit = 1;
}

message ChatMessage {
  string text = 1;
  int64 timestamp = 2;
  string sender_id = 3;
}

message BatchResponse {
  int32 created_count = 1;
}
```

---

## Example Code

### gRPC Server (Node.js)

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Load .proto file
const packageDefinition = protoLoader.loadSync('user.proto', {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const userProto = grpc.loadPackageDefinition(packageDefinition).user;

// Implement service methods
function getUser(call, callback) {
  const userId = call.request.user_id;
  const user = database.findUser(userId);

  if (!user) {
    callback({
      code: grpc.status.NOT_FOUND,
      message: 'User not found'
    });
    return;
  }

  callback(null, {
    id: user.id,
    name: user.name,
    email: user.email,
    created_at: user.createdAt
  });
}

function streamUsers(call) {
  const limit = call.request.limit || 100;
  const users = database.getAllUsers(limit);

  users.forEach(user => {
    call.write({
      id: user.id,
      name: user.name,
      email: user.email
    });
  });

  call.end();
}

// Create server
const server = new grpc.Server();

server.addService(userProto.UserService.service, {
  GetUser: getUser,
  StreamUsers: streamUsers
});

server.bindAsync(
  '0.0.0.0:50051',
  grpc.ServerCredentials.createInsecure(),
  () => {
    server.start();
    console.log('gRPC server running on port 50051');
  }
);
```

### gRPC Client (Node.js)

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Load .proto file
const packageDefinition = protoLoader.loadSync('user.proto');
const userProto = grpc.loadPackageDefinition(packageDefinition).user;

// Create client
const client = new userProto.UserService(
  'localhost:50051',
  grpc.credentials.createInsecure()
);

// Unary call
client.GetUser({ user_id: 123 }, (error, response) => {
  if (error) {
    console.error('Error:', error.message);
    return;
  }
  console.log('User:', response);
});

// Server streaming
const stream = client.StreamUsers({ limit: 10 });

stream.on('data', (user) => {
  console.log('Received user:', user);
});

stream.on('end', () => {
  console.log('Stream ended');
});

stream.on('error', (error) => {
  console.error('Stream error:', error.message);
});
```

---

## gRPC vs REST

| Feature | REST | gRPC |
|---------|------|------|
| **Protocol** | HTTP/1.1 | HTTP/2 |
| **Data Format** | JSON (text) | Protobuf (binary) |
| **API Contract** | OpenAPI/Swagger (optional) | .proto files (required) |
| **Payload Size** | Larger (JSON) | Smaller (binary, ~30% reduction) |
| **Speed** | Slower | Faster (binary + HTTP/2) |
| **Streaming** | No (need WebSockets) | Yes (4 patterns) |
| **Browser Support** | Native | Limited (need gRPC-Web) |
| **Human Readable** | Yes (JSON) | No (binary) |
| **Tooling** | curl, Postman, browser | gRPC CLI, Bloom RPC |
| **Type Safety** | Runtime validation | Compile-time |
| **Use Case** | Public APIs, CRUD | Microservices, streaming |

---

## Interview Tips

### When to Choose gRPC

**Scenario indicators:**
- "Microservices" (internal service-to-service)
- "High performance" / "Low latency"
- "Multiple languages" (polyglot environment)
- "Streaming data"
- "Internal only" (not browser-facing)

### How to Defend gRPC

> "For internal microservices communication, I'd use gRPC. It offers significant performance benefits over REST - Protocol Buffers are binary (30% smaller payloads) and HTTP/2 provides multiplexing and header compression. Strong typing via .proto files catches errors at compile time, preventing version mismatches between services. Code generation in all major languages makes it easy to add new services. For external browser-facing APIs, I'd use REST for simplicity, but for service-to-service, gRPC's performance and type safety win."

### Common Follow-Ups

**Q: "Why not use gRPC for everything?"**
A: "Limited browser support is the main reason. gRPC requires gRPC-Web proxy for browsers, adding complexity. Also, the binary format makes debugging harder - you can't just curl an endpoint. For public APIs, REST's simplicity and universal support are better. Use gRPC for internal microservices where performance matters."

**Q: "How do you handle versioning with gRPC?"**
A: "Protocol Buffers support backward and forward compatibility. Add new fields with new field numbers (never reuse numbers). Make new fields optional. Clients with old .proto files ignore new fields, and servers provide defaults for missing fields. This allows gradual rollouts without breaking changes."

**Q: "gRPC vs REST for microservices?"**
A: "For internal microservices with high traffic, gRPC's performance wins (faster, smaller payloads). For simple CRUD services with low traffic, REST is fine and simpler. Use gRPC when performance matters or you need streaming. Use REST when simplicity and debugging ease matter more."

---

## Four Communication Patterns

### 1. Unary RPC (Request-Response)
- Client sends one request, server sends one response
- Like REST, but faster
- Example: `GetUser(id) → User`

### 2. Server Streaming
- Client sends one request, server sends stream of responses
- Example: Live stock prices, log streaming
- Example: `StreamPrices(symbols) → stream of Price`

### 3. Client Streaming
- Client sends stream of requests, server sends one response
- Example: File upload in chunks, bulk data ingestion
- Example: `stream of UploadChunk → UploadResult`

### 4. Bidirectional Streaming
- Both sides send streams simultaneously
- Example: Chat, real-time gaming
- Example: `stream ChatMessage → stream ChatMessage`

---

## Connection to Your Work

Most REST/WebSocket-based systems don't use gRPC. Consider gRPC when:
- Breaking a monolith into microservices
- You need high-performance service-to-service calls
- You have multiple backend services written in different languages

**When gRPC makes sense:**
- Internal: service A <-> service B communication (gRPC)
- External: Browser/App -> API (REST or WebSockets)

---

**Key Takeaway:** gRPC is the high-performance choice for internal microservices. It's faster than REST, strongly typed, and supports streaming. Not for browser clients or public APIs, but perfect for service-to-service communication.
