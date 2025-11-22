# Webhooks

Real-time event notifications for asynchronous image processing workflows.

## Overview

Webhooks enable your application to receive instant notifications when jobs complete, instead of polling for results. This is the recommended approach for production systems.

## Benefits

- **Real-time updates**: Get notified immediately when processing completes
- **Reduced load**: No need to poll job status endpoints repeatedly
- **Scalability**: Handle thousands of concurrent jobs efficiently
- **Reliability**: Built-in retry mechanism for failed webhook deliveries

## How Webhooks Work

```
1. Configure webhook URL in pattern settings
2. Submit image processing job
3. Job processes asynchronously
4. ImgGo sends HTTP POST to your webhook URL with results
5. Your server acknowledges receipt (200 OK)
```

## Webhook Events

| Event | Trigger | Payload Includes |
|-------|---------|------------------|
| `job.completed` | Job successfully processed | Full result data |
| `job.failed` | Job processing failed | Error details |
| `job.queued` | Job added to queue (optional) | Job ID, estimated time |

## Setting Up Webhooks

### 1. Create Webhook Endpoint

**Python (Flask)**:

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

WEBHOOK_SECRET = "your_webhook_secret"

@app.route('/webhooks/imggo', methods=['POST'])
def handle_webhook():
    """Handle ImgGo webhook notifications"""

    # Verify signature
    signature = request.headers.get('X-ImgGo-Signature')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    # Parse webhook data
    data = request.json

    event_type = data['event']
    job_id = data['job_id']

    if event_type == 'job.completed':
        handle_job_completed(data)
    elif event_type == 'job.failed':
        handle_job_failed(data)

    # Return 200 OK to acknowledge receipt
    return jsonify({'status': 'received'}), 200

def verify_signature(payload, signature):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)

def handle_job_completed(data):
    """Process completed job"""
    result = data['result']

    # Store in database
    save_to_database(result)

    # Trigger downstream processes
    send_notification_email(result)

def handle_job_failed(data):
    """Handle failed job"""
    error = data['error']

    # Log error
    log_error(f"Job {data['job_id']} failed: {error}")

    # Alert admin
    send_admin_alert(error)

if __name__ == '__main__':
    app.run(port=5000)
```

**Node.js (Express)**:

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

app.post('/webhooks/imggo', (req, res) => {
  // Verify signature
  const signature = req.headers['x-imggo-signature'];
  if (!verifySignature(req.body, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const { event, job_id, result, error } = req.body;

  if (event === 'job.completed') {
    handleJobCompleted(job_id, result);
  } else if (event === 'job.failed') {
    handleJobFailed(job_id, error);
  }

  res.status(200).json({ status: 'received' });
});

function verifySignature(payload, signature) {
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(JSON.stringify(payload))
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

function handleJobCompleted(jobId, result) {
  console.log(`Job ${jobId} completed:`, result);
  // Store in database, trigger workflows, etc.
}

function handleJobFailed(jobId, error) {
  console.error(`Job ${jobId} failed:`, error);
  // Log error, send alerts, etc.
}

app.listen(5000, () => {
  console.log('Webhook server running on port 5000');
});
```

### 2. Register Webhook in ImgGo

**Via API**:

```bash
curl -X POST https://img-go.com/api/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/imggo",
    "events": ["job.completed", "job.failed"],
    "secret": "your_webhook_secret"
  }'
```

**Via Dashboard**:

1. Navigate to Settings > Webhooks
2. Click "Add Webhook"
3. Enter your webhook URL
4. Select events to subscribe to
5. Generate webhook secret
6. Click "Create"

## Webhook Payload Examples

### Job Completed

```json
{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "pattern_id": "pat_2gYc3kZ8mN",
  "status": "completed",
  "result": {
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1942.92
  },
  "confidence": 0.97,
  "processing_time_ms": 3420,
  "created_at": "2024-01-21T10:30:00Z",
  "completed_at": "2024-01-21T10:30:18Z"
}
```

### Job Failed

```json
{
  "event": "job.failed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "pattern_id": "pat_2gYc3kZ8mN",
  "status": "failed",
  "error": {
    "code": "invalid_image",
    "message": "Image URL is not accessible"
  },
  "created_at": "2024-01-21T10:30:00Z",
  "failed_at": "2024-01-21T10:30:05Z"
}
```

## Security Best Practices

### 1. Verify Webhook Signatures

Always verify the `X-ImgGo-Signature` header to ensure requests come from ImgGo:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify webhook authenticity"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)
```

### 2. Use HTTPS Only

Configure webhook URLs with HTTPS to encrypt data in transit:

```
✅ https://your-app.com/webhooks/imggo
❌ http://your-app.com/webhooks/imggo
```

### 3. Implement IP Whitelisting

Restrict webhook requests to ImgGo's IP addresses:

```nginx
# Nginx configuration
location /webhooks/imggo {
    allow 203.0.113.0/24;  # ImgGo IP range
    deny all;
    proxy_pass http://localhost:5000;
}
```

### 4. Validate Payload Schema

Validate webhook payload structure before processing:

```python
from jsonschema import validate, ValidationError

WEBHOOK_SCHEMA = {
    "type": "object",
    "properties": {
        "event": {"type": "string"},
        "job_id": {"type": "string"},
        "status": {"type": "string"}
    },
    "required": ["event", "job_id", "status"]
}

def validate_webhook_payload(data):
    """Validate webhook data structure"""
    try:
        validate(instance=data, schema=WEBHOOK_SCHEMA)
        return True
    except ValidationError:
        return False
```

## Reliability & Retry Logic

### ImgGo Retry Behavior

If your webhook endpoint fails to respond with 200 OK, ImgGo retries:

| Attempt | Delay | Total Time |
|---------|-------|------------|
| 1 | Immediate | 0s |
| 2 | 30s | 30s |
| 3 | 2 min | 2m 30s |
| 4 | 10 min | 12m 30s |
| 5 | 30 min | 42m 30s |
| 6 | 1 hour | 1h 42m 30s |

After 6 failed attempts, the webhook delivery is marked as failed.

### Idempotent Webhook Handling

Handle duplicate webhook deliveries safely:

```python
import redis

redis_client = redis.Redis()

def handle_webhook_idempotent(job_id, data):
    """Process webhook only once"""
    lock_key = f"webhook:lock:{job_id}"

    # Try to acquire lock
    if not redis_client.set(lock_key, "1", ex=3600, nx=True):
        # Already processed
        return {"status": "already_processed"}

    try:
        # Process webhook
        process_result(data)
        return {"status": "processed"}
    except Exception as e:
        # Release lock on error so it can be retried
        redis_client.delete(lock_key)
        raise
```

## Testing Webhooks

### 1. Local Testing with ngrok

Expose local server for testing:

```bash
# Install ngrok
npm install -g ngrok

# Start your local server
python app.py  # Running on localhost:5000

# Expose via ngrok
ngrok http 5000

# Use ngrok URL as webhook endpoint
# https://abc123.ngrok.io/webhooks/imggo
```

### 2. Manual Webhook Testing

Send test webhook payload:

```bash
curl -X POST https://your-app.com/webhooks/imggo \
  -H "Content-Type: application/json" \
  -H "X-ImgGo-Signature: test_signature" \
  -d '{
    "event": "job.completed",
    "job_id": "test-job-123",
    "result": {
      "test": "data"
    }
  }'
```

### 3. Automated Testing

```python
import unittest
from app import app

class WebhookTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_valid_webhook(self):
        payload = {
            "event": "job.completed",
            "job_id": "test-123",
            "result": {"test": "data"}
        }

        response = self.client.post('/webhooks/imggo', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_invalid_signature(self):
        payload = {"event": "job.completed"}

        response = self.client.post(
            '/webhooks/imggo',
            json=payload,
            headers={"X-ImgGo-Signature": "invalid"}
        )

        self.assertEqual(response.status_code, 401)
```

## Monitoring Webhook Health

### Track Webhook Success Rate

```python
from prometheus_client import Counter, Histogram

webhook_requests = Counter('webhook_requests_total', 'Total webhook requests', ['status'])
webhook_latency = Histogram('webhook_latency_seconds', 'Webhook processing time')

@app.route('/webhooks/imggo', methods=['POST'])
def handle_webhook():
    with webhook_latency.time():
        try:
            # Process webhook
            data = request.json
            handle_job_completed(data)

            webhook_requests.labels(status='success').inc()
            return jsonify({'status': 'received'}), 200

        except Exception as e:
            webhook_requests.labels(status='error').inc()
            return jsonify({'error': str(e)}), 500
```

### Set Up Alerts

```python
def check_webhook_health():
    """Alert if webhook success rate drops"""
    success_rate = get_webhook_success_rate()

    if success_rate < 0.95:  # Below 95%
        send_alert(
            f"Webhook success rate dropped to {success_rate:.1%}",
            severity="high"
        )
```

## Advanced Patterns

### Async Webhook Processing

Use background workers for long-running tasks:

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@app.route('/webhooks/imggo', methods=['POST'])
def handle_webhook():
    """Immediately acknowledge, process asynchronously"""
    data = request.json

    # Queue for background processing
    process_webhook_async.delay(data)

    # Return immediately
    return jsonify({'status': 'queued'}), 200

@celery.task
def process_webhook_async(data):
    """Process webhook in background worker"""
    if data['event'] == 'job.completed':
        result = data['result']

        # Time-consuming operations
        save_to_database(result)
        generate_pdf_report(result)
        send_email_notification(result)
        update_analytics_dashboard(result)
```

### Fan-Out Webhooks

Trigger multiple downstream systems:

```python
def handle_job_completed(data):
    """Fan out to multiple systems"""
    result = data['result']

    # Parallel execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(save_to_postgresql, result),
            executor.submit(index_in_elasticsearch, result),
            executor.submit(send_to_kafka, result),
            executor.submit(update_cache, result)
        ]

        # Wait for all to complete
        concurrent.futures.wait(futures)
```

## Troubleshooting

### Webhook Not Received

1. **Check webhook URL is accessible**:
```bash
curl -X POST https://your-app.com/webhooks/imggo
```

2. **Verify firewall allows incoming connections**

3. **Check webhook is registered**:
```bash
curl -X GET https://img-go.com/api/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY"
```

4. **Review webhook delivery logs in dashboard**

### Signature Verification Failing

- Ensure you're using the correct webhook secret
- Verify payload encoding matches (UTF-8)
- Use raw request body, not parsed JSON, for signature verification

## Next Steps

- Review [Error Handling](./error-handling.md) for webhook error scenarios
- Implement [Rate Limits](./rate-limits.md) awareness
- Explore [Integration Examples](../integration-guides) with webhooks
