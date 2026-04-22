# CRDTs (Conflict-free Replicated Data Types)

## What Is It?

A CRDT is a data structure that can be replicated across multiple nodes, edited independently and concurrently, and **guaranteed to converge** to the same state without any coordination. No central server needed to resolve conflicts - the math handles it.

**Used by:** Figma (multiplayer editing), Yjs (open-source collaborative framework), Automerge, Redis (CRDT-based replication), Riak (distributed database)

---

## The Core Problem CRDTs Solve

Same problem as OT: multiple users editing the same data simultaneously. But CRDTs solve it differently - instead of transforming operations after the fact, they design the **data structure itself** so that any order of operations produces the same result.

This property is called **commutativity** - the order doesn't matter.

---

## Two Types of CRDTs

### 1. State-based CRDTs (CvRDTs - Convergent)

- Each node maintains its own full copy of the state
- Nodes periodically **merge** their states
- The merge function must be:
  - **Commutative:** merge(A, B) = merge(B, A)
  - **Associative:** merge(A, merge(B, C)) = merge(merge(A, B), C)
  - **Idempotent:** merge(A, A) = A
- Basically: a mathematical **join-semilattice**

**Example: G-Counter (Grow-only Counter)**

3 nodes counting page views:

```
Node A: [A:5, B:0, C:0]  (A saw 5 views)
Node B: [A:0, B:3, C:0]  (B saw 3 views)
Node C: [A:0, B:0, C:7]  (C saw 7 views)

Merge: take max of each entry
Result: [A:5, B:3, C:7]
Total count: 15

Order of merges doesn't matter - always get [A:5, B:3, C:7]
```

### 2. Operation-based CRDTs (CmRDTs - Commutative)

- Instead of merging state, nodes **broadcast operations**
- Operations must be commutative (order doesn't matter)
- Requires reliable delivery (every op must reach every node, but order doesn't matter)
- More efficient on the wire (send small ops, not full state)

**Example: G-Counter as op-based**

```
Node A broadcasts: increment(A, 1)
Node B broadcasts: increment(B, 1)

Every node applies all increments.
Order doesn't matter because addition is commutative.
```

---

## Common CRDT Data Types

### Counters

| Type | Description | Use Case |
|------|-------------|----------|
| **G-Counter** | Grow only (increment) | Page views, likes |
| **PN-Counter** | Positive-negative (inc + dec) | Shopping cart quantity, upvotes/downvotes |

**PN-Counter:** Two G-Counters internally - one for increments, one for decrements. Value = P - N.

### Registers (Single Value)

| Type | Description | Use Case |
|------|-------------|----------|
| **LWW-Register** | Last-Writer-Wins (by timestamp) | User profile fields, settings |
| **MV-Register** | Multi-Value (keeps all concurrent writes) | Shows conflicts to user for manual resolution |

**LWW-Register:** Simple but lossy. If two users set a username simultaneously, one write is silently dropped based on timestamp. Good enough for many cases.

### Sets

| Type | Description | Use Case |
|------|-------------|----------|
| **G-Set** | Grow only (add, never remove) | Tag lists (if removal not needed) |
| **2P-Set** | Two-phase (add set + remove set) | Tags with removal (but can't re-add after removing) |
| **OR-Set** | Observed-Remove (add + remove freely) | Shopping carts, collaborative lists |

**OR-Set:** The most practical set CRDT. Each element gets a unique tag on add. Remove only removes the specific tags you've seen. So concurrent add + remove results in the element being present (add wins).

### Sequences (For Text Editing)

| Type | Description | Use Case |
|------|-------------|----------|
| **RGA** | Replicated Growable Array | Collaborative text editing |
| **LSEQ / Logoot** | Position-based sequences | Collaborative text editing |

These are what Figma and Yjs use internally. Each character gets a unique, ordered ID so insertions at the same position don't conflict.

---

## How CRDTs Work for Collaborative Drawing (Figma's Approach)

### The Problem
2000 users on a canvas. Each user draws shapes, moves objects, changes colors. All concurrently.

### The CRDT Approach

Each object on the canvas (shape, line, text) is a **map CRDT** with LWW-Register fields:

```
Shape_123: {
  x: LWW-Register(300, timestamp: 1001),
  y: LWW-Register(200, timestamp: 1001),
  color: LWW-Register("blue", timestamp: 1005),
  width: LWW-Register(50, timestamp: 1001)
}
```

The canvas is an **OR-Set** of shapes (add/remove shapes freely).

### Conflict Resolution

**Two users move the same shape simultaneously:**
- User A moves Shape_123 to (400, 200) at timestamp 1010
- User B moves Shape_123 to (300, 500) at timestamp 1012
- LWW-Register: User B's write wins (higher timestamp)
- Both clients converge to (300, 500)

**One user moves a shape, another deletes it:**
- With OR-Set semantics: depends on implementation
- Typically: delete wins, or last-write-wins on the existence flag
- This is a design decision, not a math constraint

**Two users add shapes at the same time:**
- OR-Set handles this trivially. Both shapes appear. No conflict.

### The Flow

```
User A draws shape     User B moves shape
       |                      |
  Local CRDT updated    Local CRDT updated
  (instant, no lag)     (instant, no lag)
       |                      |
  Broadcast op           Broadcast op
  via WebSocket          via WebSocket
       |                      |
       +-----> Server <-------+
               |     |
          Broadcast to all clients
               |     |
  Apply op to     Apply op to
  local CRDT      local CRDT
  (commutative -  (commutative -
   order doesn't   order doesn't
   matter)         matter)
```

---

## OT vs CRDTs

| Aspect | OT | CRDTs |
|--------|-----|-------|
| **How conflicts resolve** | Transform operations after the fact | Data structure prevents conflicts by design |
| **Server requirement** | Central server required for ordering | Can be fully peer-to-peer |
| **Offline support** | Limited (need server to transform) | Excellent (merge when reconnected) |
| **Implementation complexity** | Transform functions for all op combinations | Designing correct CRDT types |
| **Memory overhead** | Lower (just operations) | Higher (metadata per element - unique IDs, timestamps, tombstones) |
| **Best for text editing** | Mature, proven (Google Docs) | Catching up (Yjs, Automerge) |
| **Best for structured data** | Harder to apply | Natural fit (maps, sets, counters) |
| **Used by** | Google Docs, Google Sheets | Figma, Yjs, Automerge, Redis |

### When to Choose CRDTs Over OT

- **Offline-first apps** (mobile, intermittent connectivity)
- **Peer-to-peer** (no central server)
- **Structured data** (shapes on canvas, game state, shopping carts) rather than pure text
- **Simpler correctness guarantees** (math proves convergence)

### When to Choose OT Over CRDTs

- **Text-heavy editing** (OT is more mature here)
- **Already have a central server** (OT is simpler with a server)
- **Memory-constrained** (CRDTs carry more metadata)

---

## Tradeoffs of CRDTs

### Strengths
- **Guaranteed convergence** - mathematical proof, not just testing
- **No central server needed** - peer-to-peer capable
- **Excellent offline support** - edit offline, merge on reconnect
- **No coordination overhead** - no locks, no consensus protocols, no waiting

### Weaknesses
- **Memory overhead** - tombstones (deleted elements stay as markers), unique IDs per element, timestamps
- **Garbage collection complexity** - need to eventually clean up tombstones without breaking convergence
- **Limited conflict resolution** - LWW means some writes are silently lost. For text, character-level CRDTs can produce weird interleaving on concurrent edits
- **Harder to reason about** - the data structures are non-trivial to design correctly

---

## Interview Relevance

### When to Mention CRDTs
- Collaborative editing (drawing, documents, whiteboards)
- Offline-first applications
- Distributed counters at scale (likes, views)
- Shopping carts in distributed e-commerce
- Any "eventually consistent but must converge" scenario

### What to Say

> "For conflict resolution on the collaborative canvas, I'd use CRDTs. Each shape is represented as a map CRDT with last-writer-wins registers for properties like position and color. The canvas itself is an OR-Set of shapes so adding and removing shapes is conflict-free. The key advantage is that CRDTs are mathematically guaranteed to converge regardless of operation order, so we don't need a central server to coordinate edits. Users see their changes instantly with local-first rendering, and changes propagate via WebSockets to other clients. The tradeoff is higher memory overhead from metadata like unique IDs and tombstones for deleted elements, but for a drawing app with thousands of shapes this is manageable. If this were a pure text editor, I might lean toward Operational Transformation instead, which is more mature for character-level text editing."

### The 4 Things to Know
1. **What:** Data structures that converge without coordination
2. **Why:** Multiple users editing same data, need eventual consistency without locks
3. **Who uses it:** Figma (drawing), Yjs/Automerge (general purpose)
4. **Tradeoff vs OT:** No server needed + offline support, but higher memory overhead + LWW can silently drop writes
