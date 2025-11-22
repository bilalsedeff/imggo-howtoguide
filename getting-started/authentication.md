# Authentication Best Practices

Secure your image processing workflows with proper API key management and authentication patterns.

## Authentication Method

ImgGo uses **Bearer Token Authentication** with API keys. All requests must include an `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Getting Your API Key

1. Log in to your dashboard at [img-go.com/dashboard](https://img-go.com/dashboard)
2. Navigate to **Settings** > **API Keys**
3. Click **Generate New Key**
4. Name your key (e.g., "Production Server", "Staging Environment")
5. Copy the key immediately - it won't be shown again

## API Key Scopes and Permissions

When creating API keys, you can assign specific permissions:

| Scope | Description | Use Case |
|-------|-------------|----------|
| `patterns:read` | View patterns | Read-only access for monitoring |
| `patterns:write` | Create/update patterns | Pattern management |
| `patterns:delete` | Delete patterns | Administrative access |
| `jobs:create` | Submit processing jobs | Production processing |
| `jobs:read` | View job status and results | Retrieving processed data |
| `webhooks:manage` | Configure webhooks | Setting up event notifications |

**Principle of Least Privilege**: Only grant the minimum permissions needed. For example, a production processing server only needs `jobs:create` and `jobs:read`.

## Security Best Practices

### 1. Never Commit API Keys to Version Control

**Bad**:
```python
API_KEY = "sk_live_abc123xyz"  # NEVER DO THIS
```

**Good**:
```python
import os
API_KEY = os.environ.get("IMGGO_API_KEY")
```

### 2. Use Environment Variables

Create a `.env` file (add to `.gitignore`):

```bash
IMGGO_API_KEY=sk_live_abc123xyz
IMGGO_PATTERN_ID=pat_invoice_extractor_v1
DATABASE_URL=postgresql://user:pass@localhost/db
```

Load environment variables:

**Python**:
```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ["IMGGO_API_KEY"]
```

**Node.js**:
```javascript
require('dotenv').config();
const API_KEY = process.env.IMGGO_API_KEY;
```

### 3. Separate Keys for Different Environments

Maintain separate API keys for:

- **Development**: Limited quota, test patterns
- **Staging**: Mirror production settings
- **Production**: Full quota, production patterns

This isolates failures and prevents test data from affecting production.

### 4. Rotate Keys Regularly

Best practice: Rotate API keys every 90 days.

**Rotation Process**:
1. Generate new API key
2. Update environment variable in staging
3. Test thoroughly
4. Update production environment
5. Delete old key after 24-hour grace period

### 5. Implement Rate Limiting Client-Side

Respect rate limits to prevent throttling:

```python
import time
from functools import wraps

def rate_limit(max_per_second=10):
    min_interval = 1.0 / max_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(max_per_second=5)
def process_image(image_url):
    # API call here
    pass
```

### 6. Secure Webhook Endpoints

Verify webhook signatures to ensure requests come from ImgGo:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook request authenticity"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)

# Express.js webhook endpoint
@app.route('/webhooks/imggo', methods=['POST'])
def imggo_webhook():
    signature = request.headers.get('X-ImgGo-Signature')
    payload = request.get_data(as_text=True)

    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return {'error': 'Invalid signature'}, 401

    # Process webhook
    data = request.json
    # ...
    return {'status': 'success'}, 200
```

## Request Authentication Examples

### cURL

```bash
curl -X POST https://img-go.com/api/patterns/pat_abc/ingest \
  -H "Authorization: Bearer ${IMGGO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Python (requests)

```python
import os
import requests

API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
    headers=headers,
    json={"image_url": "https://example.com/invoice.jpg"}
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const API_KEY = process.env.IMGGO_API_KEY;
const PATTERN_ID = process.env.IMGGO_PATTERN_ID;

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

axios.post(
  `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
  { image_url: 'https://example.com/invoice.jpg' },
  { headers }
)
.then(response => console.log(response.data))
.catch(error => console.error(error.response.data));
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
    "os"
)

func main() {
    apiKey := os.Getenv("IMGGO_API_KEY")
    patternID := os.Getenv("IMGGO_PATTERN_ID")

    payload := map[string]string{
        "image_url": "https://example.com/invoice.jpg",
    }

    jsonData, _ := json.Marshal(payload)

    req, _ := http.NewRequest(
        "POST",
        "https://img-go.com/api/patterns/"+patternID+"/ingest",
        bytes.NewBuffer(jsonData),
    )

    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
}
```

## Error Handling

### 401 Unauthorized

API key is missing or invalid.

```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed. Check your API key.")
        # Log error, send alert, etc.
```

### 403 Forbidden

API key lacks necessary permissions.

```json
{
  "error": {
    "code": "insufficient_permissions",
    "message": "This API key does not have 'jobs:create' permission"
  }
}
```

**Solution**: Generate a new key with appropriate scopes.

### 429 Rate Limit Exceeded

Too many requests in a short period.

**Response Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```

**Solution**: Implement exponential backoff:

```python
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(429, 500, 502, 503, 504),
):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Usage
response = requests_retry_session().post(url, headers=headers, json=data)
```

## API Key Management Dashboard

Monitor your API key usage:

1. Navigate to **Settings** > **API Keys**
2. View for each key:
   - **Created Date**: When the key was generated
   - **Last Used**: Most recent API request
   - **Request Count**: Total requests this month
   - **Permissions**: Assigned scopes
   - **Status**: Active/Revoked

## Revoking Compromised Keys

If an API key is compromised:

1. **Immediately revoke** the key in the dashboard
2. **Generate a new key** with different permissions
3. **Update all applications** using the old key
4. **Review recent activity** for suspicious requests
5. **Enable IP whitelisting** if available

## IP Whitelisting (Enterprise)

Enterprise plans support IP whitelisting:

```bash
# Allow requests only from specific IPs
curl -X POST https://img-go.com/api/keys/key_abc/whitelist \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "allowed_ips": [
      "203.0.113.0/24",
      "198.51.100.42"
    ]
  }'
```

## Next Steps

- Learn how to [Create Your First Pattern](./first-pattern.md)
- Set up [Webhooks](../api-reference/webhooks.md) for real-time processing
- Explore [Rate Limits](../api-reference/rate-limits.md) documentation
- Implement [Error Handling](../api-reference/error-handling.md) strategies

---

**Previous**: [Quick Start Guide](./quick-start.md) | **Next**: [Create Your First Pattern](./first-pattern.md)
