# Communication Protocols Study Guide

**Purpose:** Master communication protocols for system design interviews.

---

## Files in This Directory

### Quick Reference
- **`00_OVERVIEW.md`** - Start here. Decision tree, comparison table, quick reference

### Tier 1: Must Know (Master These First)
- **`01_REST.md`** - Request-response APIs, CRUD operations
- **`02_WebSockets.md`** - Real-time bidirectional communication
- **`03_GraphQL.md`** - Flexible queries, mobile optimization

### Tier 2: Should Know (Interview Differentiators)
- **`04_SSE.md`** - Server-Sent Events, unidirectional streaming
- **`05_Webhooks.md`** - Event-driven server-to-server callbacks
- **`06_gRPC.md`** - High-performance microservices communication

### Tier 3: Nice to Know (Specialized Use Cases)
- **`07_Other_Protocols.md`** - Long Polling, Message Queues, MQTT, WebRTC

### Practice
- **`08_Practice_Scenarios.md`** - 10 detailed scenarios with solutions

---

## Study Plan

### Day 1-2: Foundation (Tier 1)
1. Read `00_OVERVIEW.md` - Get the big picture
2. Deep dive: `01_REST.md`, `02_WebSockets.md`, `03_GraphQL.md`
3. Practice: Can you explain when to use each?

### Day 3-4: Advanced (Tier 2)
1. Read: `04_SSE.md`, `05_Webhooks.md`, `06_gRPC.md`
2. Practice: Complete scenarios 1-5 in `08_Practice_Scenarios.md`

### Day 5-6: Practice & Mastery
1. Complete scenarios 6-10 in `08_Practice_Scenarios.md`
2. Practice explaining out loud (record yourself)
3. Review `00_OVERVIEW.md` decision tree until automatic

### Day 7: Mock Interview
1. Have someone ask: "Design a real-time chat app"
2. Practice your answer using the templates in each file
3. Can you confidently explain WHY and discuss tradeoffs?

---

## Interview Preparation Checklist

Before your next interview, ensure you can:

### For ANY System Design Question:
- [ ] Use the decision tree in `00_OVERVIEW.md` to pick a protocol
- [ ] Explain WHY you chose that protocol
- [ ] Discuss 2-3 alternative approaches and their tradeoffs
- [ ] Connect to your experience (work projects, personal projects)

### Tier 1 Mastery (Critical):
- [ ] **REST**: Explain when it's good, when it's bad (no real-time)
- [ ] **WebSockets**: Immediately recognize "chat", "real-time bidirectional"
- [ ] **GraphQL**: Understand mobile optimization, nested queries

### Tier 2 Knowledge (Differentiator):
- [ ] **SSE**: Know it's a simpler WebSockets for unidirectional streaming
- [ ] **Webhooks**: Understand event-driven, server-to-server pattern
- [ ] **gRPC**: Know it's for microservices, high-performance internal APIs

### Tier 3 Awareness (Bonus):
- [ ] Know Long Polling, Message Queues, MQTT, WebRTC exist
- [ ] Can mention when relevant (IoT -> MQTT, video -> WebRTC)

---

## Common Pitfall: Blanking on Real-Time Design

A frequent interview failure mode:

**Scenario:** "Design a real-time chat application."
**What goes wrong:** Candidate suggests REST, then GraphQL, eventually lands on WebSockets. They knew the right answer but couldn't access it under pressure or explain WHY.

**How these files fix this:**

1. **Pattern Recognition** (`00_OVERVIEW.md` decision tree)
   - "Real-time" + "bidirectional" = WebSockets
   - Practice until automatic

2. **WHY Explanation** (Each protocol file has a "How to Defend" section)
   - `02_WebSockets.md` has the exact answer template
   - Practice the chat question using the template

3. **Tradeoffs** (Each file has Pros/Cons table)
   - REST vs WebSockets comparison in both files
   - Practice explaining: "REST would require polling, which..."

4. **Connection to Experience** (Each file has prompts for tying protocols to your own work)

---

## How to Use These Materials

### For Quick Review (15 minutes)
1. Read `00_OVERVIEW.md`
2. Scan comparison table
3. Review decision tree

### For Deep Study (2-3 hours)
1. Pick one protocol file
2. Read thoroughly with examples
3. Try to explain it out loud
4. Complete the related practice scenario

### For Interview Prep (1 hour before)
1. Review `00_OVERVIEW.md` decision tree
2. Read "Interview Tips" section in Tier 1 files
3. Practice: "Design a chat app" answer out loud
4. Review tradeoffs for top 3 protocols

---

## Study Tips

### Active Learning
- **Don't just read** - Explain each protocol out loud
- **Use the templates** - Practice the "Interview Answer" sections
- **Record yourself** - Watch back, identify hesitations
- **Draw diagrams** - Recreate the system diagrams from memory

### Connection to Work
- How do you use WebSockets (or could you) at your day job?
- Which protocol would you use for a personal project you've built?
- Why does Slack use WebSockets? Why does Stripe use Webhooks?

### Interview Simulation
- **Practice with a timer** - Can you explain in 2 minutes?
- **Challenge yourself** - "What if we need to scale to 1M users?"
- **Tradeoff discussions** - Always mention 2+ alternatives

---

## Success Criteria

**You're ready when you can:**

1. Immediately recognize protocol from requirements
   - "Chat" -> WebSockets (instant)
   - "Payment callback" -> Webhooks (instant)
   - "Mobile bandwidth optimization" -> GraphQL (instant)

2. Explain WHY in 30 seconds
   - Use templates from each file
   - Include tradeoffs

3. Connect to experience
   - Tie it to something you've actually built or used
   - Sounds confident, not uncertain

4. Handle follow-ups
   - "How do you scale WebSockets?" -> Sticky sessions, Redis pub/sub
   - "Why not REST?" -> Polling wasteful, high latency

---

## Next Actions

After studying these materials:

1. **Practice the chat question:**
   - "Design a real-time chat application"
   - Use the template in `02_WebSockets.md`
   - Record yourself, aim for a 2-minute clear answer

2. **Complete all scenarios:**
   - Work through `08_Practice_Scenarios.md`
   - Don't skip - each teaches a different pattern

3. **Mock interview:**
   - Have someone ask random system design questions
   - Use the decision tree to pick the protocol
   - Explain reasoning confidently

---

**Remember:** You likely already know most of this material. These files help you ACCESS that knowledge under pressure and EXPLAIN it confidently with tradeoffs.

**The goal:** Never blank on "Design a real-time chat" again. WebSockets, immediately, with confidence.
