# Webhooks

**Category:** Tier 2 - Should Know

---

## Definition

**Webhooks** are server-to-server HTTP callbacks triggered by events. When something happens, one server makes an HTTP POST request to another server's endpoint.

**Think of it as:** "Reverse API" - instead of you polling for updates, the server calls YOU when something happens.

---

## Core Characteristics

- **Event-driven**: Triggered by events (payment completed, order shipped)
- **HTTP POST**: Server sends POST request to your endpoint
- **Asynchronous**: Fire-and-forget or with retries
- **Server-to-server**: Not for client apps
- **Callback pattern**: You register a URL, they call it

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Webhook Flow                             │
└─────────────────────────────────────────────────────────────┘

Setup Phase:
────────────
Your Server              Third-Party Service (Stripe)
     │                            │
     │── POST /webhooks ─────────>│  Register webhook
     │    {                       │  URL: https://yourapp.com/webhook
     │      "url": "...",         │  Events: ["payment.success"]
     │      "events": [...]       │
     │    }                       │
     │                            │
     │<─── 200 OK ────────────────│
     │     { webhook_id: "..." }  │
     │                            │


Event Happens:
──────────────
Your Server              Stripe               User
     │                     │                   │
     │                     │<─── Payment ──────│ User pays $50
     │                     │                   │
     │                 [Process Payment]       │
     │                     │                   │
     │<─── HTTP POST ──────│                   │
     │     {                                   │
     │       "event": "payment.success",       │
     │       "amount": 5000,                   │
     │       "customer": "cus_123",            │
     │       "metadata": {                     │
     │         "order_id": "ord_456"           │
     │       }                                 │
     │     }                                   │
     │                     │                   │
     │─── 200 OK ─────────>│  Acknowledge      │
     │                     │                   │
 [Update DB]              │                   │
 [Send email]             │                   │
     │                     │                   │


Retry Logic (if webhook fails):
────────────────────────────────
Your Server              Stripe
     │                     │
     │<─── POST ───────────│  Attempt 1 (immediate)
     │                     │
     │─── 500 Error ──────>│  Your server fails
     │                     │
     ... wait 1 minute ...
     │                     │
     │<─── POST ───────────│  Attempt 2 (retry)
     │                     │
     │─── 500 Error ──────>│  Still failing
     │                     │
     ... wait 5 minutes ...
     │                     │
     │<─── POST ───────────│  Attempt 3 (retry)
     │                     │
     │─── 200 OK ─────────>│  Success!
     │                     │
```

---

## Use Cases

### ✅ Perfect For

1. **Third-party integrations** (Stripe, GitHub, Twilio notify you)
2. **Payment processing** (payment completed, refund issued)
3. **CI/CD pipelines** (GitHub notifies on push, PR)
4. **Event notifications** (order shipped, email opened)
5. **Reducing polling** (instead of asking "done yet?", they tell you)

### ❌ Bad For

1. **Real-time client communication** (use WebSockets)
2. **Synchronous workflows** (webhooks are async)
3. **When you need immediate response** (network delays)
4. **Direct user interaction** (webhooks are server-to-server)

---

## Real-World Examples

1. **Stripe**: Payment completed, subscription canceled, dispute created
2. **GitHub**: Code pushed, PR opened, issue commented
3. **Twilio**: SMS received, call ended, message delivered
4. **Shopify**: Order created, product updated, refund issued
5. **Slack**: Message posted, channel created, user joined
6. **SendGrid**: Email delivered, opened, link clicked

---

## Pros and Cons

| Pros ✅ | Cons ❌ |
|---------|---------|
| No polling (efficient) | Must expose public endpoint |
| Event-driven (instant notification) | Security concerns (verify signature) |
| Scalable (server handles retries) | Debugging harder (async, retries) |
| Standard HTTP (easy to implement) | Idempotency needed (handle duplicates) |
| Reduces API calls | No guarantee of order |

---

## Example Code

### Webhook Endpoint (Node.js Express)

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// Stripe webhook endpoint
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const signature = req.headers['stripe-signature'];
  const secret = 'whsec_your_webhook_secret';

  // Verify webhook signature (CRITICAL for security)
  const payload = req.body;
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  if (signature !== `sha256=${expectedSignature}`) {
    console.error('Invalid signature');
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(payload);
  console.log(`Webhook received: ${event.type}`);

  // Handle different event types
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        const payment = event.data.object;
        console.log(`Payment successful: $${payment.amount / 100}`);

        // Update database
        await database.updateOrder(payment.metadata.order_id, {
          status: 'paid',
          payment_id: payment.id,
          paid_at: new Date()
        });

        // Send confirmation email
        await sendEmail(payment.receipt_email, 'Payment confirmed');
        break;

      case 'payment_intent.payment_failed':
        console.log('Payment failed');
        await handleFailedPayment(event.data.object);
        break;

      case 'customer.subscription.deleted':
        console.log('Subscription canceled');
        await handleSubscriptionCancellation(event.data.object);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
  } catch (error) {
    console.error('Error processing webhook:', error);
    // Return 500 so Stripe retries
    return res.status(500).send('Processing error');
  }

  // Return 200 immediately (don't make webhook wait)
  res.sendStatus(200);
});

app.listen(3000);
```

### Registering Webhook (Stripe example)

```javascript
// Register webhook with Stripe
const stripe = require('stripe')('sk_test_...');

const webhook = await stripe.webhookEndpoints.create({
  url: 'https://yourapp.com/webhook',
  enabled_events: [
    'payment_intent.succeeded',
    'payment_intent.payment_failed',
    'customer.subscription.deleted',
    'charge.refunded'
  ]
});

console.log('Webhook ID:', webhook.id);
console.log('Webhook Secret:', webhook.secret); // Save this securely!
```

---

## Best Practices

### Security

1. **Verify signatures** - Always verify webhook came from legitimate source
2. **Use HTTPS** - Encrypt data in transit
3. **Validate payload** - Check structure before processing
4. **Use webhook secrets** - Store securely (environment variables)

### Reliability

1. **Return 200 quickly** - Don't block webhook waiting for processing
2. **Process async** - Queue the work, return immediately
3. **Handle retries** - Services retry if you return non-200
4. **Idempotency** - Handle duplicate webhooks (use event IDs)
5. **Log everything** - Webhook calls, processing results, errors

### Example with Queue

```javascript
const Queue = require('bull');
const webhookQueue = new Queue('webhooks');

app.post('/webhook', async (req, res) => {
  // Verify signature...

  // Add to queue (fast)
  await webhookQueue.add('process-webhook', {
    event: req.body,
    receivedAt: Date.now()
  });

  // Return immediately
  res.sendStatus(200);
});

// Process webhooks asynchronously
webhookQueue.process('process-webhook', async (job) => {
  const { event } = job.data;

  // Check if already processed (idempotency)
  const processed = await database.checkEventProcessed(event.id);
  if (processed) {
    console.log(`Event ${event.id} already processed`);
    return;
  }

  // Process event
  await handleWebhookEvent(event);

  // Mark as processed
  await database.markEventProcessed(event.id);
});
```

---

## Interview Tips

### When to Mention Webhooks

**Scenario indicators:**
- "Third-party integration" (Stripe, GitHub, Twilio)
- "Event notification" (payment completed, order shipped)
- "Server-to-server communication"
- "Reduce polling" (don't constantly check status)

### How to Defend Webhooks

> "For payment processing with Stripe, webhooks are ideal. Instead of our server constantly polling Stripe asking 'is the payment done yet?', Stripe calls our webhook endpoint when the payment completes. This reduces API calls, provides instant notification, and is more scalable. The key considerations are security (verify webhook signatures to prevent spoofing), reliability (return 200 quickly and process async), and idempotency (handle duplicate webhooks using event IDs)."

### Common Follow-Ups

**Q: "How do you secure webhooks?"**
A: "Three layers: 1) Verify webhook signature using HMAC with a shared secret, 2) Use HTTPS to encrypt data in transit, 3) Validate payload structure before processing. Never trust the webhook data without verification - attackers can POST to your endpoint."

**Q: "What if your server is down when the webhook arrives?"**
A: "Most services (Stripe, GitHub) implement retry logic with exponential backoff. They'll retry for hours/days. When your server comes back, you receive the webhooks. Use idempotency (check event IDs) to avoid processing duplicates."

**Q: "Webhooks vs Polling?"**
A: "Webhooks are event-driven - you're notified when something happens. Polling is you repeatedly asking 'is it done yet?'. Webhooks are more efficient (fewer API calls), provide instant notification, and scale better. Use webhooks when the third-party supports them. Fall back to polling only if webhooks aren't available."

---

## Connection to Your Work

If your systems don't integrate with third parties, you may not use webhooks externally. They're still useful internally for service-to-service event notifications (e.g., a worker pinging an API when a long-running job completes).

**Common Use Case in Industry:**
- E-commerce: Stripe webhooks for payment status
- CI/CD: GitHub webhooks trigger builds
- Notifications: Email service webhooks track delivery

---

## Debugging Webhooks

### Tools

1. **ngrok** - Expose localhost for testing webhooks locally
2. **RequestBin** - Capture and inspect webhook payloads
3. **Webhook.site** - Test webhook endpoints

### Common Issues

- **Webhook not arriving**: Check firewall, HTTPS certificate
- **Signature verification failing**: Check secret, payload format
- **Timeouts**: Return 200 too slowly (queue processing)
- **Duplicate processing**: Missing idempotency checks

---

**Key Takeaway:** Webhooks are the "reverse API" pattern for server-to-server event notifications. They're essential for integrations with third-party services. Always verify signatures, return 200 quickly, and handle duplicates with idempotency.
