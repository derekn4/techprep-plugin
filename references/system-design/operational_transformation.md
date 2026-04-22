# Operational Transformation (OT)

## What Is It?

OT is a technique for maintaining consistency in collaborative editing systems. It works by **transforming operations** so they can be applied in different orders on different clients and still converge to the same result.

**Used by:** Google Docs, Google Sheets, Apache Wave (original research project)

---

## The Core Problem OT Solves

Two users are editing the same document simultaneously. User A and User B each make a change at the same time. Because of network latency, each user applies their own change first, then receives the other's change. Without transformation, the documents diverge.

### Example: Two Users Editing "ABCD"

- **User A:** Insert "X" at position 1 -> "AXBCD"
- **User B:** Delete character at position 3 (the "D") -> "ABC"

Both operations are sent to each other. Without OT:
- User A applies B's operation "delete at position 3" -> "AXBC" (deleted C, not D - WRONG)
- User B applies A's operation "insert X at position 1" -> "AXBC" (different from what A intended)

With OT, the system **transforms** the incoming operation based on what was already applied locally:
- User A receives B's "delete at 3" but knows they inserted at position 1 (before position 3), so the delete shifts to position 4 -> "AXBC" wait, let me redo this properly.

### Cleaner Example: "ABC"

Starting document: "ABC"

- **User A:** Insert "X" at position 1 -> "AXBC"
- **User B:** Insert "Y" at position 2 -> "ABYC"

Without OT, if User A applies B's "insert Y at 2":
- "AXBC" -> "AXYBC" (Y inserted at position 2, between X and B)

But User B intended Y to go between B and C. With OT:
- Transform B's operation against A's: A inserted at position 1 (before position 2), so B's position shifts to 3
- User A applies "insert Y at 3": "AXBC" -> "AXBYC"

And User B:
- Transform A's operation against B's: A inserted at position 1 (before position 2), no shift needed
- User B applies "insert X at 1": "ABYC" -> "AXBYC"

Both converge to "AXBYC".

---

## How OT Works (High Level)

### The Transform Function

OT defines a function `transform(op1, op2)` that takes two concurrent operations and returns adjusted versions:

```
transform(op1, op2) -> (op1', op2')
```

Where:
- Applying op1 then op2' gives the same result as applying op2 then op1'
- This is called the **transformation property** (TP1)

### The Operations

For text editing, operations are typically:
- **Insert(position, character)**
- **Delete(position)**
- **Retain(count)** - skip over characters (used in Google Docs)

### Architecture: Client-Server Model

```
Client A                   Server                   Client B
   |                         |                         |
   |-- op1 (insert X@1) --> |                         |
   |                         |-- op1 ----------------> |
   |                         |                         |
   |                         | <-- op2 (insert Y@2) --|
   | <-- transform(op2,op1) |                         |
   |                         |                         |
   Both clients converge     Server is source of truth
```

The server:
1. Receives operations from clients
2. Transforms them against any concurrent operations
3. Broadcasts the transformed operations to all other clients
4. Maintains a single operation history (source of truth)

---

## OT in Practice

### Google Docs Approach
- Server maintains a **revision number** for the document
- Each client sends operations tagged with the revision they're based on
- Server transforms incoming operations against all operations that happened since that revision
- Server increments revision and broadcasts the transformed operation
- Clients apply transformed operations and update their revision number

### Key Properties
- **Convergence:** All clients reach the same document state
- **Intention preservation:** Each user's edit has the intended effect (as much as possible)
- **Causality preservation:** Operations respect causal ordering

---

## Tradeoffs

### Strengths
- **Proven at scale** - Google Docs serves hundreds of millions of users
- **Fine-grained operations** - Character-level precision
- **Server authority** - Single source of truth simplifies conflict resolution

### Weaknesses
- **Complex to implement correctly** - Transform functions for all operation combinations are error-prone
- **Server dependency** - Requires a central server to order operations (not peer-to-peer)
- **Quadratic complexity risk** - Transforming against a long history of concurrent ops can get expensive
- **Hard to extend** - Adding new operation types requires new transform functions for every combination

---

## OT vs CRDTs

| Aspect | OT | CRDTs |
|--------|-----|-------|
| Architecture | Client-server (central authority) | Can be peer-to-peer |
| Complexity | Transform functions are hard to get right | Data structure design is hard, but once correct, guaranteed to work |
| Server dependency | Required for ordering | Optional |
| Offline support | Limited (need server to transform) | Excellent (merge when reconnected) |
| Used by | Google Docs, Google Sheets | Figma, Yjs, Automerge |
| Proven at scale | Yes (Google) | Yes (Figma) |

See `crdt.md` for the CRDT approach.

---

## Interview Relevance

### When to Mention OT
- Designing collaborative text editors
- Designing real-time document collaboration (Google Docs clone)
- Any system where multiple users edit the same text simultaneously

### What to Say
> "For real-time collaborative text editing, I'd use Operational Transformation. Each user's edits are represented as operations - inserts, deletes, retains. When concurrent edits happen, the server transforms incoming operations against any operations that were applied since the client's last known revision. This ensures all clients converge to the same document state. Google Docs uses this approach. The tradeoff is implementation complexity - transform functions for all operation type combinations are notoriously hard to get right - and it requires a central server for ordering. If we wanted peer-to-peer or better offline support, CRDTs would be the alternative."

### Don't Overcomplicate It
You likely won't need to implement OT in an interview. Know:
1. **What it is** - Transforming concurrent operations so they converge
2. **Why it exists** - Multiple users editing same data simultaneously
3. **Who uses it** - Google Docs
4. **Tradeoff vs CRDTs** - Central server vs peer-to-peer, complexity tradeoffs
