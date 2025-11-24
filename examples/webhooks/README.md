# ImgGo Webhooks Example

This example demonstrates how to use webhooks with the ImgGo API.

## Overview

Webhooks allow you to receive real-time notifications when job processing completes,
eliminating the need for polling.

## Webhook Events

ImgGo supports the following webhook events:

| Event | Description |
|-------|-------------|
| `job.succeeded` | Job completed successfully |
| `job.failed` | Job failed to process |

## Setup

### 1. Install Dependencies

```bash
pip install flask requests
```

### 2. Set Environment Variables

```bash
export IMGGO_API_KEY=your_api_key_here
export WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Run the Webhook Server

```bash
python webhook-example.py
```

### 4. Expose Your Server (for testing)

Use ngrok to expose your local server:

```bash
ngrok http 5000
```

### 5. Register Your Webhook

```python
from webhook_example import create_webhook

result = create_webhook(
    url="https://your-ngrok-url.ngrok.io/webhook",
    events=["job.succeeded", "job.failed"]
)
print(result)
```

Or use curl:

```bash
curl -X POST https://img-go.com/api/webhooks \
  -H "Authorization: Bearer $IMGGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["job.succeeded", "job.failed"],
    "secret": "your_webhook_secret"
  }'
```

## Webhook Payload

When a job completes, ImgGo sends a POST request to your webhook URL:

### job.succeeded

```json
{
  "event": "job.succeeded",
  "data": {
    "job_id": "abc123",
    "pattern_id": "xyz789",
    "status": "succeeded",
    "result": {
      "field1": "value1",
      "field2": "value2"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### job.failed

```json
{
  "event": "job.failed",
  "data": {
    "job_id": "abc123",
    "pattern_id": "xyz789",
    "status": "failed",
    "error": "Error message"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Signature Verification

ImgGo signs webhook payloads using HMAC-SHA256 with your webhook secret.
The signature is included in the `X-ImgGo-Signature` header.

```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Best Practices

1. **Always verify signatures** - Ensure webhook requests are from ImgGo
2. **Respond quickly** - Return 200 within 5 seconds to avoid retries
3. **Process async** - Queue webhook processing for complex operations
4. **Handle duplicates** - Webhooks may be delivered multiple times
5. **Use HTTPS** - Always use secure endpoints in production
