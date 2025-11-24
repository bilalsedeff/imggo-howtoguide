# Performance Optimization

This guide covers strategies to optimize performance when using the ImgGo API at scale.

## Table of Contents

- [Understanding Performance](#understanding-performance)
- [Image Optimization](#image-optimization)
- [Concurrency and Parallelism](#concurrency-and-parallelism)
- [Caching Strategies](#caching-strategies)
- [Network Optimization](#network-optimization)
- [Rate Limit Management](#rate-limit-management)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Cost Optimization](#cost-optimization)

## Understanding Performance

### Key Metrics

#### 1. Throughput**

- Images processed per hour/day
- Target: 1000+ images/hour for batch processing

#### 2. Latency**

- Time from upload to result
- Typical: 2-10 seconds per image
- Factors: image size, pattern complexity, API load

#### 3. Success Rate**

- Percentage of successful extractions
- Target: >99% success rate

#### 4. Cost per Image**

- API calls + infrastructure costs
- Optimize to reduce per-unit cost

## Image Optimization

### 1. Resize Images

Large images increase upload time and processing time.

**Optimal Size:**

- Max dimension: 2048px
- File size: <2MB
- Format: JPEG with 85% quality

**Implementation:**

```python
from PIL import Image

def optimize_image(input_path, output_path, max_size=2048):
    """Resize and compress image for optimal processing."""
    img = Image.open(input_path)

    # Convert RGBA to RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    # Resize if too large
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    # Save with optimization
    img.save(output_path, 'JPEG', quality=85, optimize=True)

    original_size = os.path.getsize(input_path)
    optimized_size = os.path.getsize(output_path)
    reduction = (1 - optimized_size / original_size) * 100

    print(f"Reduced size by {reduction:.1f}%")

# Usage
optimize_image('large_invoice.png', 'optimized_invoice.jpg')
```

**Results:**

- 50-80% file size reduction
- 30-50% faster upload
- No significant accuracy loss

### 2. Choose the Right Format

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| JPEG | Photos, documents | Small size, fast | Lossy compression |
| PNG | Screenshots, diagrams | Lossless | Large file size |
| WebP | Modern use cases | Best compression | Limited support |
| PDF | Multi-page documents | Industry standard | Larger files |

**Recommendation:** Convert to JPEG before upload unless transparency is required.

### 3. Remove Unnecessary Metadata

```python
from PIL import Image

def strip_metadata(image_path):
    """Remove EXIF data to reduce file size."""
    img = Image.open(image_path)
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)
    image_without_exif.save(image_path)
```

### 4. Crop Irrelevant Areas

If only part of the image contains relevant data:

```python
def crop_to_content(image_path, crop_box):
    """Crop image to relevant area.

    Args:
        crop_box: (left, top, right, bottom) in pixels
    """
    img = Image.open(image_path)
    cropped = img.crop(crop_box)
    cropped.save(image_path)

# Example: Crop top half of image
img = Image.open('receipt.jpg')
width, height = img.size
crop_to_content('receipt.jpg', (0, 0, width, height // 2))
```

## Concurrency and Parallelism

### 1. Concurrent Uploads

Process multiple images simultaneously.

**Python (asyncio):**

See [`examples/languages/python/async-batch.py`](../../examples/languages/python/async-batch.py) for complete implementation.

```python
import asyncio
import aiohttp

async def process_batch(image_paths, pattern_id, max_concurrent=10):
    """Process images with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(image_path):
        async with semaphore:
            return await upload_and_poll(image_path, pattern_id)

    results = await asyncio.gather(*[process_one(path) for path in image_paths])
    return results
```

**Performance:**

- Sequential: 100 images = 500 seconds (5s per image)
- Concurrent (10): 100 images = 50 seconds (10x faster)

**Node.js (Promise.all):**

See [`examples/languages/nodejs/async-batch.ts`](../../examples/languages/nodejs/async-batch.ts)

```typescript
async function processBatch(imagePaths: string[], patternId: string) {
  const MAX_CONCURRENT = 10;

  for (let i = 0; i < imagePaths.length; i += MAX_CONCURRENT) {
    const chunk = imagePaths.slice(i, i + MAX_CONCURRENT);
    const results = await Promise.all(
      chunk.map(path => processImage(path, patternId))
    );
    console.log(`Processed ${i + chunk.length}/${imagePaths.length}`);
  }
}
```

### 2. Optimal Concurrency Level

Finding the right concurrency level:

```python
import time

def benchmark_concurrency(image_paths, pattern_id):
    """Test different concurrency levels."""
    concurrency_levels = [1, 5, 10, 20, 50]

    for level in concurrency_levels:
        start = time.time()
        results = process_batch(image_paths, pattern_id, max_concurrent=level)
        duration = time.time() - start

        print(f"Concurrency {level}: {duration:.2f}s ({len(image_paths)/duration:.1f} images/s)")

# Results example:
# Concurrency 1:  500.00s (0.2 images/s)
# Concurrency 5:  100.00s (1.0 images/s)
# Concurrency 10: 50.00s  (2.0 images/s)  <- Optimal
# Concurrency 20: 52.00s  (1.9 images/s)  <- Diminishing returns
# Concurrency 50: 55.00s  (1.8 images/s)  <- Too high, overhead increases
```

**Recommendation:** Start with 10 concurrent requests, adjust based on your rate limits.

### 3. Worker Pool Pattern

For long-running services:

```python
from concurrent.futures import ThreadPoolExecutor

def process_with_workers(image_paths, pattern_id, num_workers=10):
    """Process images using worker pool."""
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_image, path, pattern_id)
            for path in image_paths
        ]

        results = []
        for future in futures:
            try:
                result = future.result(timeout=120)
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")

        return results
```

## Caching Strategies

### 1. Result Caching

Cache extraction results to avoid reprocessing identical images:

```python
import hashlib
import json
import os

CACHE_DIR = './cache'

def get_image_hash(image_path):
    """Generate hash of image file."""
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_cached_result(image_path, pattern_id):
    """Get cached result if available."""
    image_hash = get_image_hash(image_path)
    cache_key = f"{image_hash}-{pattern_id}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)

    return None

def cache_result(image_path, pattern_id, result):
    """Save result to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    image_hash = get_image_hash(image_path)
    cache_key = f"{image_hash}-{pattern_id}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    with open(cache_file, 'w') as f:
        json.dump(result, f)

def process_with_cache(image_path, pattern_id):
    """Process image with caching."""
    # Check cache
    cached = get_cached_result(image_path, pattern_id)
    if cached:
        print(f"Cache hit: {image_path}")
        return cached

    # Process
    print(f"Cache miss: {image_path}")
    result = process_image(image_path, pattern_id)

    # Save to cache
    cache_result(image_path, pattern_id, result)

    return result
```

**Results:**

- Cache hit: <1ms (instant)
- Cache miss: 2-10s (normal processing)

### 2. Redis Caching

For distributed systems:

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result_redis(image_hash, pattern_id, ttl=86400):
    """Get cached result from Redis."""
    cache_key = f"imggo:{image_hash}:{pattern_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    return None

def cache_result_redis(image_hash, pattern_id, result, ttl=86400):
    """Save result to Redis with TTL."""
    cache_key = f"imggo:{image_hash}:{pattern_id}"
    redis_client.setex(cache_key, ttl, json.dumps(result))
```

### 3. Cache Invalidation

Clear cache when pattern is updated:

```python
def clear_pattern_cache(pattern_id):
    """Clear all cached results for a pattern."""
    import glob

    pattern = os.path.join(CACHE_DIR, f"*-{pattern_id}.json")
    for cache_file in glob.glob(pattern):
        os.remove(cache_file)
        print(f"Removed: {cache_file}")
```

## Network Optimization

### 1. Use URL Processing

For cloud-stored images, use URL processing instead of downloading and uploading:

**Slow (download + upload):**

```python
# Download from S3
response = requests.get(s3_url)
with open('temp.jpg', 'wb') as f:
    f.write(response.content)

# Upload to ImgGo
result = upload_image('temp.jpg', pattern_id)
```

**Fast (direct URL):**

```python
# Process directly from URL
result = process_url(s3_url, pattern_id)
```

**Performance:**

- 50-70% faster (no download needed)
- Lower bandwidth costs
- Simpler code

### 2. Connection Pooling

Reuse HTTP connections:

```python
import requests

# Create session with connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)
session.mount('https://', adapter)

# Reuse session for multiple requests
for image in images:
    response = session.post(url, files={'image': open(image, 'rb')})
```

### 3. Compression

Enable gzip compression:

```python
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept-Encoding': 'gzip, deflate'
}
```

Most HTTP clients enable this by default.

### 4. Regional Endpoints

If available, use geographically closer endpoints:

```python
# US East
IMGGO_BASE_URL = 'https://us-east.img-go.com/api'

# EU
IMGGO_BASE_URL = 'https://eu.img-go.com/api'

# Asia Pacific
IMGGO_BASE_URL = 'https://ap.img-go.com/api'
```

## Rate Limit Management

### 1. Exponential Backoff

Handle rate limits gracefully:

```python
import time

def request_with_backoff(func, max_retries=5):
    """Execute function with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            wait_time = min(2 ** attempt, e.retry_after or 60)
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
```

See [`examples/languages/python/error-handling.py`](../../examples/languages/python/error-handling.py) for complete implementation.

### 2. Token Bucket Algorithm

Distribute requests evenly:

```python
import time

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate, capacity):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def acquire(self):
        """Wait until a token is available."""
        while True:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return

            # Wait for next token
            time.sleep((1 - self.tokens) / self.rate)

# Usage: 10 requests per second, burst of 20
limiter = RateLimiter(rate=10, capacity=20)

for image in images:
    limiter.acquire()
    process_image(image, pattern_id)
```

### 3. Distributed Rate Limiting

For multi-server deployments, use Redis:

```python
import redis
import time

class DistributedRateLimiter:
    """Distributed rate limiter using Redis."""

    def __init__(self, redis_client, key, rate, window=60):
        self.redis = redis_client
        self.key = key
        self.rate = rate
        self.window = window

    def acquire(self):
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window

        # Remove old entries
        self.redis.zremrangebyscore(self.key, 0, window_start)

        # Count requests in window
        count = self.redis.zcard(self.key)

        if count < self.rate:
            # Allow request
            self.redis.zadd(self.key, {str(now): now})
            self.redis.expire(self.key, self.window)
            return True

        return False
```

## Monitoring and Metrics

### 1. Track Performance Metrics

```python
import time
import statistics

class PerformanceTracker:
    """Track API performance metrics."""

    def __init__(self):
        self.latencies = []
        self.successes = 0
        self.failures = 0

    def record_request(self, start_time, success):
        """Record request metrics."""
        latency = time.time() - start_time
        self.latencies.append(latency)

        if success:
            self.successes += 1
        else:
            self.failures += 1

    def get_stats(self):
        """Calculate statistics."""
        return {
            'total_requests': len(self.latencies),
            'success_rate': self.successes / len(self.latencies) * 100,
            'avg_latency': statistics.mean(self.latencies),
            'p50_latency': statistics.median(self.latencies),
            'p95_latency': statistics.quantiles(self.latencies, n=20)[18],
            'p99_latency': statistics.quantiles(self.latencies, n=100)[98],
        }

# Usage
tracker = PerformanceTracker()

for image in images:
    start = time.time()
    try:
        result = process_image(image, pattern_id)
        tracker.record_request(start, True)
    except Exception:
        tracker.record_request(start, False)

print(tracker.get_stats())
```

### 2. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('imggo.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('imggo')

logger.info(f"Processing {image_path} with pattern {pattern_id}")
logger.info(f"Job created: {job_id} (latency: {latency:.2f}s)")
logger.error(f"Job failed: {error}")
```

### 3. Alerting

Set up alerts for issues:

```python
def check_health(tracker):
    """Alert on performance degradation."""
    stats = tracker.get_stats()

    if stats['success_rate'] < 95:
        send_alert(f"Success rate dropped to {stats['success_rate']:.1f}%")

    if stats['p95_latency'] > 15:
        send_alert(f"P95 latency increased to {stats['p95_latency']:.1f}s")
```

## Cost Optimization

### 1. Deduplicate Images

Avoid processing duplicates:

```python
import hashlib

processed_hashes = set()

def should_process(image_path):
    """Check if image has already been processed."""
    image_hash = get_image_hash(image_path)

    if image_hash in processed_hashes:
        print(f"Skipping duplicate: {image_path}")
        return False

    processed_hashes.add(image_hash)
    return True

for image in images:
    if should_process(image):
        process_image(image, pattern_id)
```

### 2. Batch Similar Images

Group similar images and use optimized patterns:

```python
# Group by document type
invoices = [img for img in images if 'invoice' in img]
receipts = [img for img in images if 'receipt' in img]

# Process in batches
process_batch(invoices, pattern_id='pat_invoice_123')
process_batch(receipts, pattern_id='pat_receipt_456')
```

### 3. Use Webhooks for Long-Running Jobs

Avoid polling overhead:

```python
# Submit job with webhook
response = requests.post(
    f"{API_URL}/patterns/{pattern_id}/ingest",
    files={'image': open(image_path, 'rb')},
    json={'webhook_url': 'https://myapp.com/webhook/imggo'}
)

# Receive result via webhook (no polling needed)
@app.route('/webhook/imggo', methods=['POST'])
def handle_webhook():
    data = request.json
    if data['status'] == 'succeeded':
        save_result(data['result'])
```

## Performance Checklist

- [ ] Optimize image sizes (<2MB, <2048px)
- [ ] Use concurrent processing (10-20 concurrent requests)
- [ ] Implement result caching
- [ ] Use URL processing for cloud-stored images
- [ ] Enable connection pooling
- [ ] Handle rate limits with exponential backoff
- [ ] Deduplicate images before processing
- [ ] Track performance metrics
- [ ] Set up monitoring and alerting
- [ ] Use webhooks for async processing

## Next Steps

- [Pattern Design Best Practices](./pattern-design-best-practices.md)
- [Security Best Practices](./security-best-practices.md)
- [Production Deployment](./production-deployment.md)

## Need Help?

- [API Reference](../api-reference/)
- [Examples](../../examples/)
- GitHub Issues
