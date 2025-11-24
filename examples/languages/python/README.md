# Python Examples

Production-ready Python code examples for the ImgGo API.

## Installation

```bash
cd examples/languages/python
pip install -r requirements.txt
```

## Setup

Set your API key as an environment variable:

```bash
export IMGGO_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```
IMGGO_API_KEY=your_api_key_here
IMGGO_BASE_URL=https://img-go.com/api
```

## Examples

### 1. Basic Upload (`basic-upload.py`)

Upload an image file directly and get results.

**When to use:**
- Simple, one-off image processing
- Desktop applications with local files
- Getting started

**Usage:**
```bash
python basic-upload.py path/to/image.jpg PATTERN_ID
```

**Example:**
```bash
python basic-upload.py ../../test-images/invoice1.jpg pat_invoice_abc123
```

**Features:**
- Direct file upload
- Synchronous polling
- Simple error handling

---

### 2. URL Processing (`url-processing.py`)

Process images from public URLs (S3, CDN, cloud storage).

**When to use:**
- Cloud-based workflows
- Images already hosted elsewhere
- Email attachment processing
- S3/CloudFront integration

**Usage:**
```bash
python url-processing.py <image_url> PATTERN_ID
```

**Example:**
```bash
python url-processing.py https://my-cdn.com/invoices/inv001.jpg pat_invoice_abc123
```

**Features:**
- Process remote images
- No file downloads required
- Ideal for serverless

---

### 3. Error Handling (`error-handling.py`)

Production-ready example with comprehensive error handling.

**When to use:**
- Production deployments
- High-reliability requirements
- Network-unstable environments

**Usage:**
```bash
python error-handling.py path/to/image.jpg PATTERN_ID
```

**Features:**
- Automatic retry with exponential backoff
- Rate limit handling
- Timeout management
- Idempotency keys
- Custom exceptions
- Result validation

**Error Handling:**
- `429 Rate Limit` → Waits for `Retry-After` header
- `5xx Server Errors` → Retries with exponential backoff
- `4xx Client Errors` → Fails immediately (don't retry)
- `Connection Errors` → Retries with backoff
- `Timeouts` → Retries with backoff

---

### 4. Async Batch Processing (`async-batch.py`)

Process multiple images concurrently using `asyncio`.

**When to use:**
- Batch processing workflows
- High-volume processing (100s-1000s of images)
- Time-sensitive processing

**Usage:**
```bash
python async-batch.py PATTERN_ID image1.jpg image2.jpg image3.jpg ...
```

**Example:**
```bash
python async-batch.py pat_invoice_abc123 invoice*.jpg
```

**Features:**
- Concurrent uploads
- Concurrent polling
- Batch progress tracking
- Results saved to JSON file
- Summary statistics

**Performance:**
- Process 100 images in parallel
- 10-20x faster than sequential processing
- Memory efficient streaming

---

## Code Patterns

### Pattern 1: Simple Upload

```python
import requests

def upload_image(image_path, pattern_id):
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"https://img-go.com/api/patterns/{pattern_id}/ingest",
            files={"image": f},
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
    return response.json()["data"]["job_id"]
```

### Pattern 2: Polling with Timeout

```python
import time

def poll_job(job_id, max_attempts=60):
    for _ in range(max_attempts):
        response = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        data = response.json()["data"]

        if data["status"] == "succeeded":
            return data["manifest"]
        elif data["status"] == "failed":
            raise Exception(data["error"])

        time.sleep(2)
```

### Pattern 3: URL Processing

```python
def process_url(image_url, pattern_id):
    response = requests.post(
        f"https://img-go.com/api/patterns/{pattern_id}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"image_url": image_url}
    )
    return response.json()["data"]["job_id"]
```

### Pattern 4: Error Handling with Retry

```python
import time

def upload_with_retry(image_path, pattern_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return upload_image(image_path, pattern_id)
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## Best Practices

### 1. Always Use Idempotency Keys

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Idempotency-Key": f"unique-request-id-{image_hash}"
}
```

Prevents duplicate processing if request is retried.

### 2. Set Timeouts

```python
response = requests.post(url, files=files, timeout=30)
```

Prevents hanging connections.

### 3. Validate Results

```python
result = data["manifest"]
if not result or not result.get("required_field"):
    raise ValueError("Invalid result")
```

### 4. Use Context Managers

```python
with open(image_path, 'rb') as f:
    response = requests.post(url, files={"image": f})
```

Ensures files are properly closed.

### 5. Log Everything in Production

```python
import logging

logging.info(f"Processing {image_path} with pattern {pattern_id}")
logging.info(f"Job created: {job_id}")
logging.error(f"Job failed: {error}")
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: `ValueError: IMGGO_API_KEY environment variable not set`

**Solution:**
```bash
export IMGGO_API_KEY="your_key_here"
```

### Issue: `FileNotFoundError: [Errno 2] No such file or directory`

**Solution:** Use absolute paths or check current working directory:
```python
import os
print(os.getcwd())  # Check where script is running from
```

### Issue: `JSONDecodeError: Expecting value`

**Cause:** API returned non-JSON response (usually HTML error page)

**Solution:** Check API key is valid, check response status code:
```python
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
```

## Next Steps

- See [Use Cases](../../../use-cases/) for complete end-to-end examples
- See [Formats](../../formats/) for output format examples
- See [Integrations](../../../integrations/) for database/automation setup

## Need Help?

- [API Reference](../../../docs/api-reference/)
- [Getting Started Guide](../../../docs/getting-started/)
- GitHub Issues
