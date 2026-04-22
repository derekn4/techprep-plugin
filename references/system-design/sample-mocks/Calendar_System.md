# System Design: Calendar System

**Source:** Common system design interview question

---

## Overview

Design a calendar system like Google Calendar or Calendly. Users create events, invite others, check availability, and get reminders. The core challenges: **conflict detection, recurring events, timezone handling, and real-time sync across devices.**

---

## Clarifying Questions & Answers

| Question | Answer |
|----------|--------|
| Is this a personal calendar, shared/team calendar, or scheduling tool? | All three - personal + shared + scheduling |
| How many users? | ~50 million |
| Do we need recurring events? | Yes (daily, weekly, monthly, custom) |
| Multi-timezone support? | Yes, users travel and collaborate across timezones |
| Real-time sync across devices? | Yes, changes should appear on all devices quickly |
| Do we need "find a time" / availability checking? | Yes |
| Calendar sharing / permissions? | Yes (view only, edit, full access) |
| Reminders / notifications? | Yes (email, push, in-app) |
| Integration with external calendars (Google, Outlook)? | Nice-to-have, not core |

---

## Requirements

### Functional
- **CRUD events** - create, read, update, delete single and recurring events
- **Invite attendees** - send invitations, track RSVPs (accept/decline/tentative)
- **Recurring events** - daily, weekly, monthly, custom patterns + exceptions
- **Availability lookup** - "find a time" across multiple users
- **Reminders** - configurable notifications before events
- **Calendar sharing** - permissions (view/edit) for other users
- **Multi-device sync** - changes reflect everywhere in real-time

### Non-Functional
- **Low read latency:** Calendar view loads in <200ms
- **Consistency:** No double-bookings (conflicts detected)
- **Availability:** 99.99% uptime (people depend on calendars)
- **Scalability:** 50M users, each with potentially thousands of events
- **Durability:** Never lose someone's events

---

## High-Level Design

```
 ┌──────────────┐     ┌──────┐     ┌───────────────┐
 │   Clients    │────►│  LB  │────►│  API Gateway   │
 │ web/mob/desk │     └──────┘     └───────┬────────┘
 └──────┬───────┘                          │
        │                    ┌─────────────┼──────────────┬────────────────┐
        │                    ▼             ▼              ▼                ▼
        │            ┌──────────────┐ ┌──────────┐ ┌────────────┐ ┌────────────┐
        │            │ Event        │ │  Query   │ │Notification│ │   Sync     │
        │            │ Service      │ │ Service  │ │  Service   │ │  Service   │
        │            │(CRUD,conflict│ │(calendar │ │            │ │            │
        │            │  detection)  │ │  views)  │ │            │ │            │
        │            └──────┬───────┘ └────┬─────┘ └─────┬──────┘ └─────┬──────┘
        │                   │              │             │               │
        │                   ▼              ▼             │          ┌────▼─────┐
        │            ┌──────────────────────────┐        │          │WebSocket │
        │            │   PostgreSQL             │        │          │Pub/Sub   │
        │            │  (events, attendees,     │        │          │(Redis)   │
        │            │   recurrence rules)      │        │          └──────────┘
        │            └────────────┬─────────────┘        │
        │                        │                       ▼
        │                        ▼              ┌─────────────────┐
        │                 ┌────────────┐        │ Reminder        │
        │                 │Redis Cache │        │ Scheduler       │
        │                 │(calendar   │        │ (sorted set in  │
        │                 │ views,     │        │  Redis, scanned │
        │                 │ free/busy) │        │  by workers)    │
        │                 └────────────┘        └────────┬────────┘
        │                                                │
        │                                                ▼
  ┌─────▼──────┐                                ┌────────────────┐
  │ WebSocket  │◄───────────────────────────────│  Push / Email  │
  │ connection │   real-time sync to devices    │  Notification  │
  └────────────┘                                └────────────────┘

Write path: Client -> API Gateway -> Event Service -> Postgres (conflict check) -> Cache invalidate
                                                   -> Kafka -> Notification Service + Sync Service
Read path:  Client -> API Gateway -> Query Service -> Redis Cache -> (miss) -> Postgres
```

### Data Flow

**Create event:**
1. Client sends event details to Event Service
2. Service checks for conflicts (query overlapping events)
3. If no conflict, write to DB
4. Send invitations to attendees (async via queue)
5. Schedule reminders
6. Push update to all connected devices via WebSocket

**View calendar (week view):**
1. Client requests events for date range
2. Query Service fetches from cache (Redis) or DB
3. Expand recurring events into instances for the requested range
4. Return merged list sorted by time

---

## Deep Dive

### 1. Data Model

**Events table:**
```
events
├── event_id (PK)
├── creator_id (FK → users)
├── title, description, location
├── start_time (UTC timestamp)
├── end_time (UTC timestamp)
├── timezone (IANA string, e.g., "America/Los_Angeles")
├── is_recurring (boolean)
├── recurrence_rule (RFC 5545 RRULE string, nullable)
├── recurrence_group_id (links recurring instances)
├── created_at, updated_at
```

**Attendees table:**
```
event_attendees
├── event_id (FK)
├── user_id (FK)
├── status (invited / accepted / declined / tentative)
├── role (organizer / required / optional)
```

**Why SQL (PostgreSQL)?**
- Events have strong relationships (attendees, recurrences, exceptions)
- Need ACID for conflict detection (no double-booking)
- Range queries are common (`WHERE start_time BETWEEN x AND y`)
- Index on `(user_id, start_time)` for fast calendar views

### 2. Recurring Events (The Hard Part)

**Option A: Store the rule, expand on read**
- Store one row with RRULE: `FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20261231`
- On query, expand the rule into individual instances for the date range
- Pros: Storage efficient, easy to update the whole series
- Cons: Expansion is CPU work on every read

**Option B: Pre-generate instances**
- Generate individual event rows for next N months
- Background job extends further into the future as time passes
- Pros: Fast reads (just query like normal events)
- Cons: More storage, editing "all future events" requires updating many rows

**Recommendation:** Hybrid - store the rule AND pre-generate instances for the next 6 months. Query pre-generated for speed, fall back to rule expansion for distant dates.

**Exceptions:** "Delete just this one" or "move this occurrence to Thursday"
- Store exceptions table: `(recurrence_group_id, original_date, action: skip|modify, modified_event_id)`

### 3. Conflict Detection

```sql
SELECT * FROM events e
JOIN event_attendees ea ON e.event_id = ea.event_id
WHERE ea.user_id = ?
  AND e.start_time < ? -- new event end time
  AND e.end_time > ?   -- new event start time
```

- Use a **database transaction** with SELECT FOR UPDATE to prevent race conditions
- Two people booking the same slot simultaneously → one wins, one gets conflict error
- For "find a time": run this query for each candidate slot across all attendees

### 4. Timezone Handling

- **Store everything in UTC** in the database
- **Store the original timezone** alongside (for display and recurring event expansion)
- **Convert to user's local timezone** on the client
- Recurring events: "Every Monday at 9am Pacific" must account for DST changes
  - Expand using the original timezone, THEN convert to UTC

### 5. Real-Time Sync

**WebSocket connections** for instant updates:
- Each client maintains a WebSocket to Sync Service
- When an event is created/updated/deleted, publish to a **pub/sub channel** (Redis Pub/Sub or Kafka)
- Sync Service pushes to all connected devices of affected users
- Fallback: polling every 30-60s if WebSocket disconnects

### 6. Reminders

- When event is created, schedule reminder jobs: `(event_id, user_id, remind_at)`
- **Reminder Scheduler** scans for reminders due in next minute, sends them
- Use a priority queue or sorted set in Redis: `ZADD reminders <timestamp> <event_id:user_id>`
- Worker polls: `ZRANGEBYSCORE reminders 0 <now>`

### 7. Availability / "Find a Time"

1. Collect all attendees' events for the target date range
2. Build a "busy intervals" list per attendee
3. Find gaps where ALL attendees are free
4. Return suggested slots ranked by preference (working hours, shorter gaps first)

**Optimization:** Cache "free/busy" blocks per user per day. Invalidate when events change.

---

## Key Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| SQL vs NoSQL | SQL wins here - relationships, transactions for conflicts, range queries. NoSQL adds complexity for little benefit |
| Recurring: rule-only vs pre-generate | Rule-only saves storage but costs CPU on reads. Pre-generate is fast reads but more storage/complexity |
| WebSocket vs polling for sync | WebSocket = instant but more infra. Polling = simpler but delayed |
| UTC storage + timezone metadata | Correct but adds complexity for DST edge cases in recurring events |
| Availability as precomputed cache vs on-demand | Cache = fast but stale. On-demand = fresh but slower for large groups |

---

## Email + Calendar Product Angle

If the interviewer frames this as a calendar feature inside an email client (a common product integration), think:
- Scheduling features (AI-powered scheduling) live inside the email UI
- Calendar + email integration: "Schedule a meeting" from within an email thread -> needs availability checking
- Speed matters: calendar views must load instantly in the inbox
- Calendar data needs to sync with the email client in real-time
