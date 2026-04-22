# REST (Representational State Transfer)

**Category:** Tier 1 - Must Know

---

## Definition

**REST** is an architectural style for web APIs using HTTP methods to perform operations on resources.

---

## Core Characteristics

- **Request-Response model**: Client sends request, server responds, connection closes
- **Stateless**: Each request is independent (no server-side session)
- **Resource-based**: URLs represent resources (`/users/123`)
- **HTTP methods**: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- **Text-based**: Usually JSON or XML

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     REST API Flow                           │
└─────────────────────────────────────────────────────────────┘

Client (Browser/Mobile)          REST API Server
      │                                 │
      │── GET /api/users/123 ──────────>│
      │    Headers: Authorization       │
      │                                 │
      │                           ┌─────────┐
      │                           │Database │
      │                           │Query    │
      │                           └─────────┘
      │                                 │
      │<─── 200 OK ─────────────────────│
      │     {                           │
      │       "id": 123,                │
      │       "name": "Alice",          │
      │       "email": "alice@..."      │
      │     }                           │
      │                                 │
      Connection closes

      Time passes...

      │── POST /api/users ─────────────>│
      │    Body: { "name": "Bob" }      │
      │                                 │
      │<─── 201 Created ────────────────│
      │     { "id": 124, ... }          │
      │                                 │
      Connection closes
```

---

## Use Cases

### ✅ Perfect For

1. **CRUD operations** - Create, Read, Update, Delete resources
   - User management, product catalogs, blog posts
   - Example: `GET /products`, `POST /orders`, `PUT /users/42`

2. **Public APIs** - Third-party integrations (easy to document)
   - Twitter API, Stripe API, GitHub API
   - Well-documented standards (OpenAPI/Swagger)

3. **Cacheable data** - Product catalogs, user profiles
   - HTTP caching reduces server load
   - Data that doesn't change often

4. **Simple request-response** - Form submissions, file uploads
   - Traditional web patterns
   - One request, one response

5. **Standard web apps** - Traditional server-rendered pages
   - Most common architecture
   - Team familiarity

### ❌ Bad For

1. **Real-time updates** - Chat, live notifications (requires polling)
2. **High-frequency data** - Stock tickers updating every second
3. **Server-initiated communication** - Server can't push without client request

---

## Real-World Examples

1. **Twitter API**: `GET /tweets/{id}`, `POST /tweets`, `DELETE /tweets/{id}`
2. **Stripe API**: `POST /charges`, `GET /customers/{id}`
3. **GitHub API**: `GET /repos/{owner}/{repo}`, `POST /issues`
4. **E-commerce**: Product listings, shopping cart, checkout

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| Simple and widely understood | Not real-time (need polling) |
| Works everywhere (universal HTTP support) | High overhead (HTTP headers ~500 bytes each request) |
| Cacheable (HTTP caching built-in) | Chatty (multiple requests for related data) |
| Stateless (easy to scale) | Over-fetching/under-fetching data |
| Great tooling (Postman, Swagger, curl) | No server push (polling wastes bandwidth) |

---

## REST for "Real-Time" (Polling - The Wrong Approach)

### Short Polling

```
Client repeatedly asks "any new messages?"

Client                          Server
   │                               │
   │──── GET /messages ──────────>│  (empty)
   │<─── 200: [] ─────────────────│
   │                               │
   ... wait 1 second ...
   │                               │
   │──── GET /messages ──────────>│  (empty)
   │<─── 200: [] ─────────────────│
   │                               │
   ... wait 1 second ...
   │                               │
   │──── GET /messages ──────────>│  (new message!)
   │<─── 200: ["Hello!"] ─────────│
```

**Problems:**
- ⚠️ Wastes bandwidth (90% of requests return nothing)
- ⚠️ High latency (up to 1 second delay)
- ⚠️ Server load (1000 clients = 1000 requests/sec)
- ⚠️ Not scalable

---

## Example Code

### Client (JavaScript fetch)

```javascript
// GET request
const response = await fetch('https://api.example.com/users/123', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'application/json'
  }
});
const user = await response.json();

// POST request
const newUser = await fetch('https://api.example.com/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Alice', email: 'alice@example.com' })
});
```

### Server (Node.js Express)

```javascript
const express = require('express');
const app = express();

// GET endpoint
app.get('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  const user = database.findUser(userId);
  res.json(user);
});

// POST endpoint
app.post('/api/users', (req, res) => {
  const newUser = database.createUser(req.body);
  res.status(201).json(newUser);
});

app.listen(3000);
```

---

## Interview Tips

**When to mention REST:**
- Default choice for most APIs
- Always consider REST first, then justify why you need something else

**How to defend REST:**
- "REST is simple, standard, and cacheable - perfect for CRUD operations"
- "For a product catalog, REST is ideal because data doesn't change often and HTTP caching reduces load"

**When to NOT use REST:**
- "For real-time chat, REST polling would waste bandwidth and introduce latency - WebSockets are better"
- "For complex nested queries on mobile, GraphQL reduces API calls and over-fetching"

---

## Common Patterns

### RESTful URL Structure

```
GET    /users           # List all users
POST   /users           # Create new user
GET    /users/123       # Get user 123
PUT    /users/123       # Update user 123 (full replace)
PATCH  /users/123       # Update user 123 (partial)
DELETE /users/123       # Delete user 123

GET    /users/123/posts # Get posts by user 123
POST   /users/123/posts # Create post for user 123
```

### HTTP Status Codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **204 No Content**: Success, no body to return
- **400 Bad Request**: Invalid request
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but no permission
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

---

## Connection to Your Work

Think about where REST fits naturally in systems you've built:
- Device or resource management APIs
- `GET /devices`, `POST /devices/{id}/connect`
- Standard CRUD operations for configuration and admin flows

**Common interview failure mode:**
- Candidate suggests REST for real-time chat (wrong)
- Should immediately recognize: "Chat = real-time = WebSockets"
- REST would require polling (wasteful)

---

**Key Takeaway:** REST is the default choice for request-response APIs. Only move to other protocols when REST's limitations (no real-time, chatty) become problems.
