# Error Handling

Comprehensive guide to API error codes, common issues, and resolution strategies.

## Error Response Format

All API errors follow a consistent JSON format:

```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human-readable error description",
    "details": {
      "field": "Additional context"
    }
  },
  "request_id": "req_abc123xyz"
}
```

## HTTP Status Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 202 | Accepted | Job queued for processing |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary outage |

## Common Errors

### Authentication Errors

#### 401: Missing API Key

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "missing_authorization",
    "message": "Authorization header is required"
  }
}
```

**Solution**:

```bash
# Include Authorization header
curl -H "Authorization: Bearer YOUR_API_KEY" ...
```

#### 401: Invalid API Key

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "invalid_api_key",
    "message": "API key is invalid or has been revoked"
  }
}
```

**Solutions**:

- Verify API key is correct
- Check if key has been revoked in dashboard
- Generate a new API key if needed

#### 403: Insufficient Permissions

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "insufficient_permissions",
    "message": "This API key does not have 'patterns:write' permission"
  }
}
```

**Solution**: Create new API key with required scopes in dashboard.

### Validation Errors

#### 422: Invalid Schema

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "invalid_schema",
    "message": "Schema validation failed",
    "details": {
      "field": "line_items",
      "issue": "Expected array, received string"
    }
  }
}
```

**Solution**: Ensure schema matches pattern definition.

#### 400: Missing Required Field

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "missing_field",
    "message": "Required field 'image_url' is missing"
  }
}
```

**Solution**: Include all required fields in request.

### Image Processing Errors

#### 400: Invalid Image URL

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "invalid_image_url",
    "message": "Image URL is not accessible or format is unsupported",
    "details": {
      "url": "https://example.com/image.jpg",
      "http_status": 404
    }
  }
}
```

**Solutions**:

- Verify URL is publicly accessible
- Check image format (supports: JPG, PNG, PDF, WEBP)
- Ensure no authentication required for URL

#### 400: Image Too Large

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "image_too_large",
    "message": "Image exceeds maximum file size of 10MB",
    "details": {
      "file_size_mb": 15.2,
      "max_size_mb": 10
    }
  }
}
```

**Solution**: Compress or resize image before uploading.

#### 422: Image Quality Too Low

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "low_image_quality",
    "message": "Image quality is too low for accurate extraction",
    "details": {
      "resolution": "480x640",
      "recommended_min_resolution": "1024x768"
    }
  }
}
```

**Solution**: Use higher resolution images (minimum 1024x768 recommended).

### Rate Limiting Errors

#### 429: Rate Limit Exceeded

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_at": "2024-01-21T11:00:00Z"
    }
  }
}
```

**Response Headers**:

```plaintext
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

**Solution**: Implement exponential backoff retry logic.

### Resource Errors

#### 404: Pattern Not Found

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "pattern_not_found",
    "message": "Pattern 'pat_xyz123' does not exist"
  }
}
```

**Solutions**:

- Verify pattern ID is correct
- Check pattern hasn't been deleted
- Ensure you have access to this pattern

#### 404: Job Not Found

**Error**:

```json
{
  "success": false,
  "error": {
    "code": "job_not_found",
    "message": "Job not found or has expired"
  }
}
```

**Note**: Jobs expire after 30 days.

## Error Handling Best Practices

### 1. Implement Retry Logic with Exponential Backoff

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_retry_session():
    """Create session with automatic retries"""
    session = requests.Session()

    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# Usage
session = create_retry_session()
response = session.post(url, headers=headers, json=data)
```

### 2. Handle Specific Error Codes

```python
def process_image(image_url):
    """Process image with comprehensive error handling"""
    try:
        response = requests.post(
            f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"image_url": image_url}
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_data = e.response.json()

        if status_code == 401:
            # Authentication error
            log_error("Invalid API key")
            send_alert_to_admin()
            raise

        elif status_code == 429:
            # Rate limit exceeded
            retry_after = int(e.response.headers.get('Retry-After', 60))
            log_warning(f"Rate limited. Retrying after {retry_after}s")
            time.sleep(retry_after)
            return process_image(image_url)  # Retry

        elif status_code == 422:
            # Validation error
            log_error(f"Validation failed: {error_data['error']['message']}")
            return None  # Skip this image

        elif status_code >= 500:
            # Server error - retry with backoff
            log_error(f"Server error: {error_data['error']['message']}")
            time.sleep(5)
            return process_image(image_url)

        else:
            # Other errors
            log_error(f"Unexpected error: {error_data}")
            raise

    except requests.exceptions.ConnectionError:
        log_error("Network connection failed")
        time.sleep(10)
        return process_image(image_url)  # Retry

    except requests.exceptions.Timeout:
        log_error("Request timeout")
        return None
```

### 3. Validate Before Sending

```python
def validate_image_url(url):
    """Validate image URL before processing"""
    import re
    from urllib.parse import urlparse

    # Check URL format
    if not re.match(r'^https?://', url):
        raise ValueError("URL must start with http:// or https://")

    # Check URL is accessible
    try:
        response = requests.head(url, timeout=5)
        response.raise_for_status()
    except:
        raise ValueError(f"Image URL is not accessible: {url}")

    # Check content type
    content_type = response.headers.get('Content-Type', '')
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']

    if not any(ct in content_type for ct in allowed_types):
        raise ValueError(f"Unsupported content type: {content_type}")

    # Check file size
    content_length = int(response.headers.get('Content-Length', 0))
    max_size = 10 * 1024 * 1024  # 10MB

    if content_length > max_size:
        raise ValueError(f"Image too large: {content_length / 1024 / 1024:.1f}MB")

    return True
```

### 4. Use Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Prevent cascading failures"""
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

# Usage
breaker = CircuitBreaker()

try:
    result = breaker.call(process_image, image_url)
except Exception as e:
    log_error(f"Circuit breaker prevented call: {e}")
```

### 5. Log Errors with Context

```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_api_error(error_response, context):
    """Log API errors with full context"""
    logging.error(json.dumps({
        'event': 'api_error',
        'error_code': error_response.get('error', {}).get('code'),
        'error_message': error_response.get('error', {}).get('message'),
        'request_id': error_response.get('request_id'),
        'context': context,
        'timestamp': time.time()
    }))
```

## Testing Error Scenarios

### Simulate Errors for Testing

```python
# Test invalid API key
response = requests.post(url, headers={"Authorization": "Bearer invalid_key"})
assert response.status_code == 401

# Test missing image_url
response = requests.post(url, headers=headers, json={})
assert response.status_code == 400

# Test rate limiting (send many requests rapidly)
for i in range(1100):
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 429:
        print("Rate limit triggered as expected")
        break
```

## Monitoring & Alerts

### Set Up Error Rate Monitoring

```python
from prometheus_client import Counter, Histogram

api_errors = Counter('api_errors_total', 'Total API errors', ['error_code'])
api_latency = Histogram('api_latency_seconds', 'API request latency')

def monitored_api_call(func):
    """Decorator to monitor API calls"""
    def wrapper(*args, **kwargs):
        with api_latency.time():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if hasattr(e, 'response'):
                    error_code = e.response.json().get('error', {}).get('code')
                    api_errors.labels(error_code=error_code).inc()
                raise
    return wrapper

@monitored_api_call
def process_image(image_url):
    # API call here
    pass
```

## Next Steps

- Review [Rate Limits](./rate-limits.md) to avoid throttling
- Set up [Webhooks](./webhooks.md) for async error handling
- Implement [Authentication](../getting-started/authentication.md) best practices
