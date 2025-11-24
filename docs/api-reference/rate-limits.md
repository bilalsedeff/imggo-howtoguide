# Rate Limits

Understanding and working within API rate limits for optimal performance and cost efficiency.

## Rate Limit Tiers

Rate limits are enforced based on your subscription plan:

| Plan | Requests/Month | Requests/Minute | Burst Limit |
|------|----------------|-----------------|-------------|
| Free | 50 | 5 | 10 |
| Starter | 500 | 10 | 20 |
| Pro | 5,000 | 50 | 100 |
| Business | 50,000 | 200 | 500 |
| Enterprise | Custom | Custom | Custom |

**Note**: Limits are per API key. Multiple API keys can be used to increase throughput.

## Rate Limit Headers

Every API response includes rate limit information in headers:

```plaintext
X-RateLimit-Limit: 5000          # Total requests allowed in period
X-RateLimit-Remaining: 4847      # Requests remaining
X-RateLimit-Reset: 1640995200    # Unix timestamp when limit resets
```

## Checking Rate Limits

```python
import requests
from datetime import datetime

response = requests.get(
    "https://img-go.com/api/patterns",
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# Parse rate limit headers
limit = int(response.headers.get('X-RateLimit-Limit'))
remaining = int(response.headers.get('X-RateLimit-Remaining'))
reset = int(response.headers.get('X-RateLimit-Reset'))

reset_time = datetime.fromtimestamp(reset)

print(f"Rate Limit: {remaining}/{limit} requests remaining")
print(f"Resets at: {reset_time}")

# Calculate usage percentage
usage_percent = ((limit - remaining) / limit) * 100
print(f"Usage: {usage_percent:.1f}%")
```

## Rate Limit Exceeded Response

When you exceed your rate limit:

**Status Code**: `429 Too Many Requests`

**Response**:

```json
{
  "success": false,
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "details": {
      "limit": 5000,
      "remaining": 0,
      "reset_at": "2024-01-21T11:00:00Z"
    }
  }
}
```

**Headers**:

```plaintext
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

## Best Practices

### 1. Implement Request Throttling

Limit request rate client-side to avoid hitting limits:

```python
import time
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.max_requests = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_request_time
        wait_time = self.min_interval - elapsed

        if wait_time > 0:
            time.sleep(wait_time)

        self.last_request_time = time.time()

# Usage
limiter = RateLimiter(max_requests_per_second=10)  # 10 req/sec

for image_url in image_urls:
    limiter.wait_if_needed()
    process_image(image_url)
```

### 2. Exponential Backoff for 429 Errors

Retry with increasing delays:

```python
import time
import random

def api_call_with_backoff(func, max_retries=5):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt == max_retries - 1:
                    raise  # Final attempt failed

                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)

                # Use Retry-After header if provided
                retry_after = e.response.headers.get('Retry-After')
                if retry_after:
                    wait_time = max(wait_time, int(retry_after))

                print(f"Rate limited. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                raise

# Usage
result = api_call_with_backoff(lambda: process_image(image_url))
```

### 3. Monitor Usage Proactively

Alert before hitting limits:

```python
def check_rate_limit_usage(headers):
    """Alert if approaching rate limit"""
    limit = int(headers.get('X-RateLimit-Limit'))
    remaining = int(headers.get('X-RateLimit-Remaining'))

    usage_percent = ((limit - remaining) / limit) * 100

    if usage_percent > 90:
        send_alert(
            f"Rate limit usage at {usage_percent:.1f}%",
            severity="high"
        )
    elif usage_percent > 75:
        send_alert(
            f"Rate limit usage at {usage_percent:.1f}%",
            severity="medium"
        )

# After each request
response = make_api_request()
check_rate_limit_usage(response.headers)
```

### 4. Use Request Queuing

Queue requests to smooth out bursts:

```python
import queue
import threading
import time

class RequestQueue:
    def __init__(self, max_requests_per_second):
        self.queue = queue.Queue()
        self.max_rps = max_requests_per_second
        self.running = True

        # Start worker thread
        self.worker = threading.Thread(target=self._process_queue)
        self.worker.start()

    def _process_queue(self):
        """Process queued requests at controlled rate"""
        interval = 1.0 / self.max_rps

        while self.running:
            try:
                func, args, kwargs = self.queue.get(timeout=1)

                # Execute request
                func(*args, **kwargs)

                # Rate limit
                time.sleep(interval)

            except queue.Empty:
                continue

    def enqueue(self, func, *args, **kwargs):
        """Add request to queue"""
        self.queue.put((func, args, kwargs))

    def shutdown(self):
        """Stop processing queue"""
        self.running = False
        self.worker.join()

# Usage
request_queue = RequestQueue(max_requests_per_second=10)

for image_url in image_urls:
    request_queue.enqueue(process_image, image_url)

# Wait for queue to empty
while not request_queue.queue.empty():
    time.sleep(1)

request_queue.shutdown()
```

## Strategies for High-Volume Processing

### 1. Batch Processing

Group images and process during off-peak hours:

```python
from datetime import datetime

def is_off_peak():
    """Check if current time is off-peak"""
    hour = datetime.now().hour
    return hour < 8 or hour > 20  # Before 8am or after 8pm

def batch_process_images(image_urls, batch_size=100):
    """Process images in batches"""
    for i in range(0, len(image_urls), batch_size):
        batch = image_urls[i:i + batch_size]

        # Wait for off-peak if needed
        while not is_off_peak():
            time.sleep(300)  # Check every 5 minutes

        # Process batch
        for url in batch:
            process_image(url)
```

### 2. Multiple API Keys

Distribute load across multiple API keys:

```python
import itertools

API_KEYS = [
    "key_1",
    "key_2",
    "key_3"
]

# Round-robin key selection
key_cycle = itertools.cycle(API_KEYS)

def process_with_rotating_keys(image_urls):
    """Distribute requests across multiple keys"""
    for image_url in image_urls:
        api_key = next(key_cycle)

        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"image_url": image_url}
        )

        # Handle response
```

### 3. Priority Queuing

Process high-priority items first:

```python
import heapq

class PriorityRequestQueue:
    def __init__(self):
        self.queue = []
        self.counter = 0

    def add(self, func, priority=5, *args, **kwargs):
        """Add request with priority (lower = higher priority)"""
        heapq.heappush(
            self.queue,
            (priority, self.counter, func, args, kwargs)
        )
        self.counter += 1

    def process(self):
        """Process queue in priority order"""
        while self.queue:
            priority, _, func, args, kwargs = heapq.heappop(self.queue)
            func(*args, **kwargs)
            time.sleep(0.1)  # Rate limit

# Usage
priority_queue = PriorityRequestQueue()

# High priority (urgent invoices)
priority_queue.add(process_image, priority=1, url=urgent_invoice_url)

# Normal priority (regular processing)
priority_queue.add(process_image, priority=5, url=regular_invoice_url)

# Low priority (archival processing)
priority_queue.add(process_image, priority=10, url=archive_url)

priority_queue.process()
```

## Enterprise Solutions

For processing volumes exceeding standard plans:

### 1. Contact Sales for Custom Limits

Enterprise plans offer:

- Custom rate limits (1,000+ requests/minute)
- Dedicated infrastructure
- SLA guarantees
- Priority support

### 2. Webhook-Based Processing

Use webhooks instead of polling to avoid extra API calls:

```python
# Instead of polling (uses API calls)
while True:
    status = check_job_status(job_id)  # API call
    if status == "completed":
        break
    time.sleep(2)

# Use webhooks (no polling needed)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data['event'] == 'job.completed':
        process_result(data['result'])
```

### 3. Caching

Cache results for frequently processed images:

```python
import hashlib
import redis

redis_client = redis.Redis()
CACHE_TTL = 86400  # 24 hours

def get_image_hash(image_url):
    """Generate hash for image URL"""
    return hashlib.sha256(image_url.encode()).hexdigest()

def process_image_with_cache(image_url):
    """Check cache before processing"""
    cache_key = f"result:{get_image_hash(image_url)}"

    # Check cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    # Not in cache, process
    result = process_image(image_url)

    # Store in cache
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(result)
    )

    return result
```

## Monitoring & Analytics

### Track Rate Limit Usage Over Time

```python
from prometheus_client import Gauge

rate_limit_remaining = Gauge('rate_limit_remaining', 'Remaining API requests')
rate_limit_usage_percent = Gauge('rate_limit_usage_percent', 'Rate limit usage %')

def update_rate_limit_metrics(headers):
    """Update Prometheus metrics"""
    limit = int(headers.get('X-RateLimit-Limit'))
    remaining = int(headers.get('X-RateLimit-Remaining'))

    usage_percent = ((limit - remaining) / limit) * 100

    rate_limit_remaining.set(remaining)
    rate_limit_usage_percent.set(usage_percent)

# After each request
response = make_api_request()
update_rate_limit_metrics(response.headers)
```

### Daily Usage Reports

```python
def generate_usage_report():
    """Generate daily rate limit usage report"""
    total_requests = get_daily_request_count()
    monthly_limit = 5000

    usage_percent = (total_requests / monthly_limit) * 100
    days_remaining = (datetime.now().replace(day=1, month=datetime.now().month + 1) - datetime.now()).days
    projected_usage = (total_requests / datetime.now().day) * 30

    report = f"""
    Daily Rate Limit Usage Report
    =============================
    Today: {total_requests} requests
    Monthly Limit: {monthly_limit}
    Current Usage: {usage_percent:.1f}%
    Projected Monthly: {projected_usage:.0f} requests
    Status: {'WARNING: On track to exceed' if projected_usage > monthly_limit else 'OK: Within limits'}
    """

    send_email_report(report)
```

## Testing Rate Limits

```python
def test_rate_limit_handling():
    """Test rate limit error handling"""
    # Rapidly send requests to trigger rate limit
    for i in range(100):
        try:
            response = make_api_request()
            print(f"Request {i}: Success")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Request {i}: Rate limited (expected)")
                assert 'Retry-After' in e.response.headers
                break
        time.sleep(0.01)
```

## Next Steps

- Review [Error Handling](./error-handling.md) for rate limit errors
- Set up [Webhooks](./webhooks.md) to reduce polling
- Implement [Monitoring](../integration-guides/monitoring.md) for usage tracking
