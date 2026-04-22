# GraphQL

**Category:** Tier 1 - Must Know

---

## Definition

**GraphQL** is a query language for APIs where clients specify exactly what data they need, and servers return only that data.

---

## Core Characteristics

- **Single endpoint**: One URL for all queries (`POST /graphql`)
- **Client-defined queries**: Client specifies data shape
- **Strongly typed schema**: GraphQL schema defines available data
- **No over-fetching**: Get exactly what you ask for
- **No under-fetching**: Get related data in one query

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GraphQL Flow                             │
└─────────────────────────────────────────────────────────────┘

Traditional REST (multiple requests):
──────────────────────────────────────
Client                              Server
  │                                    │
  │── GET /users/123 ─────────────────>│
  │<─── { id, name, email } ───────────│
  │                                    │
  │── GET /users/123/posts ───────────>│
  │<─── [{ id, title }, ...] ──────────│
  │                                    │
  │── GET /posts/1/comments ──────────>│
  │<─── [{ id, text }, ...] ───────────│
  │                                    │
3 requests, lots of unnecessary data


GraphQL (single request):
──────────────────────────
Client                              Server
  │                                    │
  │── POST /graphql ──────────────────>│
  │    query {                         │
  │      user(id: 123) {         ┌──────────┐
  │        name                  │ Resolvers│
  │        posts(limit: 5) {     │ fetch    │
  │          title               │ data     │
  │          comments(limit: 3) {└──────────┘
  │            text                    │
  │          }                         │
  │        }                           │
  │      }                             │
  │    }                               │
  │                                    │
  │<─── Exactly the data requested ────│
  │     {                              │
  │       "user": {                    │
  │         "name": "Alice",           │
  │         "posts": [                 │
  │           {                        │
  │             "title": "Post 1",     │
  │             "comments": [...]      │
  │           }                        │
  │         ]                          │
  │       }                            │
  │     }                              │
  │                                    │
1 request, exact data needed
```

---

## Use Cases

### ✅ Perfect For

1. **Mobile apps** - Reduce API calls, save bandwidth
2. **Complex nested data** - User + posts + comments in one query
3. **Multiple clients** - iOS, Android, Web query differently
4. **Rapid frontend iteration** - Frontend changes don't need backend changes
5. **Aggregating microservices** - Single GraphQL gateway

### ❌ Bad For

1. **Simple CRUD** - REST is simpler
2. **File uploads** - GraphQL not designed for this
3. **When you need HTTP caching** - All requests are POST
4. **Real-time updates** - GraphQL is request-response (need subscriptions or WebSockets)

---

## Real-World Examples

1. **GitHub API v4**: Query repos, issues, PRs in single request
2. **Shopify**: Product catalog with flexible queries
3. **Meta (Facebook)**: News feed, profiles (created GraphQL)
4. **Yelp**: Business listings with reviews, photos
5. **Airbnb**: Listings with availability, reviews, host info

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| No over-fetching (specify exact fields) | Learning curve (new paradigm) |
| No under-fetching (get related data in one query) | No HTTP caching (everything is POST) |
| Strongly typed (compile-time validation) | Complex queries can be expensive |
| Self-documenting (schema is documentation) | N+1 query problem (need DataLoader) |
| Frontend flexibility (no backend changes) | File uploads are complex |

---

## Example Code

### GraphQL Query (Client)

```javascript
// Query with nested data
const query = `
  query GetUserWithPosts($userId: ID!) {
    user(id: $userId) {
      name
      email
      posts(limit: 5) {
        title
        createdAt
        comments(limit: 3) {
          text
          author {
            name
          }
        }
      }
    }
  }
`;

const response = await fetch('https://api.example.com/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query,
    variables: { userId: '123' }
  })
});

const { data } = await response.json();
console.log(data.user.posts);
```

### GraphQL Server (Node.js with Apollo)

```javascript
const { ApolloServer, gql } = require('apollo-server');

// Schema definition
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    comments: [Comment!]!
  }

  type Comment {
    id: ID!
    text: String!
    author: User!
  }

  type Query {
    user(id: ID!): User
    posts(limit: Int): [Post!]!
  }
`;

// Resolvers (how to fetch data)
const resolvers = {
  Query: {
    user: (parent, { id }) => database.findUser(id),
    posts: (parent, { limit }) => database.getPosts(limit)
  },
  User: {
    posts: (user) => database.getPostsByUser(user.id)
  },
  Post: {
    author: (post) => database.findUser(post.authorId),
    comments: (post) => database.getCommentsByPost(post.id)
  }
};

const server = new ApolloServer({ typeDefs, resolvers });
server.listen().then(({ url }) => console.log(`Server at ${url}`));
```

---

## GraphQL vs REST

| Feature | REST | GraphQL |
|---------|------|---------|
| **Endpoints** | Many (`/users`, `/posts`) | One (`/graphql`) |
| **Data shape** | Server decides | Client decides |
| **Over-fetching** | Common (get whole object) | No (specify fields) |
| **Under-fetching** | Common (need multiple requests) | No (one query) |
| **Multiple resources** | Multiple requests | Single request |
| **Caching** | HTTP caching | Custom caching needed |
| **Learning curve** | Low | Medium-High |
| **File uploads** | Easy | Complex |
| **Versioning** | `/v1/`, `/v2/` | Schema evolution |

---

## Interview Tips

### When to Choose GraphQL

**Scenario indicators:**
- "Mobile app with limited bandwidth"
- "Multiple clients with different data needs"
- "Complex nested data structures"
- "Reduce number of API calls"

### How to Defend GraphQL

> "For a mobile app with complex data requirements, GraphQL eliminates over-fetching and reduces API calls. Instead of making 3 REST requests to get user + posts + comments, the mobile client makes one GraphQL query specifying exactly what fields it needs. This saves bandwidth and reduces latency. The trade-off is increased backend complexity and lack of HTTP caching, but for mobile use cases where bandwidth is expensive, it's worth it."

### Common Follow-Ups

**Q: "How do you handle caching with GraphQL?"**
A: "Since GraphQL uses POST requests, standard HTTP caching doesn't work. Solutions include: client-side caching (Apollo Client normalizes data), server-side caching (DataLoader batches and caches), and CDN caching with persisted queries (query IDs map to query strings)."

**Q: "What's the N+1 problem?"**
A: "When resolving nested data, you might make N+1 database queries - one for the parent, then one per child. For example, fetching 10 users and their posts could be 1 query for users + 10 queries for posts. DataLoader solves this by batching requests within a single tick."

---

## Connection to Your Work

Think about where GraphQL could fit in systems you've built:
- Mobile app needs flexible queries over the same backend
- Different screens need different subsets of the same data
- Reducing bandwidth or request count for clients on slow networks

**When NOT to use GraphQL:**
- Real-time updates -> WebSockets (not GraphQL queries)
- Simple CRUD admin/management -> REST is simpler

---

**Key Takeaway:** GraphQL shines for complex, nested queries and mobile bandwidth optimization. Choose it when clients need flexibility and you want to reduce API calls. Stick with REST for simple CRUD.
