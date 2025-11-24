# cURL Examples

Production-ready bash scripts using cURL for the ImgGo API.

## Prerequisites

- `curl` command-line tool (pre-installed on most Unix systems)
- `bash` shell
- `grep`, `sed`, `awk` (standard Unix tools)

## Setup

Set your API key as an environment variable:

```bash
export IMGGO_API_KEY="your_api_key_here"
```

Or add to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export IMGGO_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## Examples

### 1. Basic Upload (`basic-upload.sh`)

Upload an image file directly and get results.

**When to use:**

- Command-line automation
- Quick API testing
- Shell scripts
- CI/CD pipelines
- Cron jobs

**Usage:**

```bash
chmod +x basic-upload.sh
./basic-upload.sh path/to/image.jpg PATTERN_ID
```

**Example:**

```bash
./basic-upload.sh ../../test-images/invoice1.jpg pat_invoice_abc123
```

**Features:**

- Direct file upload using multipart/form-data
- Synchronous polling
- Simple error handling
- Exit codes (0 = success, 1 = error)

---

### 2. URL Processing (`url-processing.sh`)

Process images from public URLs (S3, CDN, cloud storage).

**When to use:**

- Cloud-based workflows
- Images already hosted elsewhere
- Webhook automation
- S3/CloudFront integration
- CI/CD image validation

**Usage:**

```bash
chmod +x url-processing.sh
./url-processing.sh <image_url> PATTERN_ID
```

**Example:**

```bash
./url-processing.sh https://my-cdn.com/invoices/inv001.jpg pat_invoice_abc123
```

**Features:**

- Process remote images
- No file downloads required
- URL validation
- JSON payload

---

### 3. Error Handling (`error-handling.sh`)

Production-ready example with comprehensive error handling.

**When to use:**

- Production deployments
- High-reliability requirements
- Automated pipelines
- Scheduled jobs

**Usage:**

```bash
chmod +x error-handling.sh
./error-handling.sh path/to/image.jpg PATTERN_ID
```

**Features:**

- Automatic retry with exponential backoff
- Rate limit handling (429 status codes)
- HTTP status code checking
- Idempotency keys to prevent duplicates
- Result validation
- Detailed error messages

**Error Handling:**

- `429 Rate Limit` → Waits for `Retry-After` header duration
- `5xx Server Errors` → Retries with exponential backoff (1s, 2s, 4s, ...)
- `4xx Client Errors` → Fails immediately (don't retry invalid requests)
- Connection Errors → Retries with backoff

---

## cURL Patterns

### Pattern 1: Simple File Upload

```bash
curl -X POST "https://img-go.com/api/patterns/PATTERN_ID/ingest" \
  -H "Authorization: Bearer $IMGGO_API_KEY" \
  -F "image=@path/to/image.jpg"
```

### Pattern 2: URL Processing

```bash
curl -X POST "https://img-go.com/api/patterns/PATTERN_ID/ingest" \
  -H "Authorization: Bearer $IMGGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Pattern 3: Check Job Status

```bash
curl -X GET "https://img-go.com/api/jobs/JOB_ID" \
  -H "Authorization: Bearer $IMGGO_API_KEY"
```

### Pattern 4: Upload with Idempotency Key

```bash
curl -X POST "https://img-go.com/api/patterns/PATTERN_ID/ingest" \
  -H "Authorization: Bearer $IMGGO_API_KEY" \
  -H "Idempotency-Key: unique-request-id-123" \
  -F "image=@path/to/image.jpg"
```

### Pattern 5: Capture HTTP Status Code

```bash
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "URL" -H "..." -F "...")
HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 200 ]; then
  echo "Success"
fi
```

### Pattern 6: Extract JSON Field

```bash
# Extract job_id
JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

# Extract status
STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
```

### Pattern 7: Polling Loop

```bash
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT + 1))

  RESPONSE=$(curl -s "https://img-go.com/api/jobs/$JOB_ID" -H "...")
  STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

  if [ "$STATUS" = "succeeded" ]; then
    echo "Success!"
    break
  fi

  sleep 2
done
```

### Pattern 8: Exponential Backoff

```bash
MAX_RETRIES=3
retry=0

while [ $retry -lt $MAX_RETRIES ]; do
  retry=$((retry + 1))

  # Make request
  RESPONSE=$(curl -s "URL")

  if [ $? -eq 0 ]; then
    break
  fi

  # Exponential backoff: 1s, 2s, 4s
  WAIT_TIME=$((2 ** (retry - 1)))
  sleep $WAIT_TIME
done
```

## Best Practices

### 1. Always Use Idempotency Keys

```bash
IDEMPOTENCY_KEY="upload-$(basename "$IMAGE_PATH")-$PATTERN_ID-$(date +%s)"

curl -X POST "..." \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -F "image=@$IMAGE_PATH"
```

Prevents duplicate processing if script is run multiple times.

### 2. Check Exit Codes

```bash
set -e  # Exit on any error

# Or check manually:
if [ $? -ne 0 ]; then
  echo "Error occurred"
  exit 1
fi
```

### 3. Validate Inputs

```bash
if [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: File not found"
  exit 1
fi

if [[ ! "$IMAGE_URL" =~ ^https?:// ]]; then
  echo "Error: Invalid URL"
  exit 1
fi
```

### 4. Set Timeouts

```bash
curl --max-time 30 "URL"  # 30 second timeout
```

### 5. Silent Mode with Status

```bash
curl -s -w "\n%{http_code}" "URL"  # Silent but show HTTP code
```

### 6. Log Everything

```bash
echo "[$(date)] Processing $IMAGE_PATH" >> process.log
echo "[$(date)] Job created: $JOB_ID" >> process.log
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Process Images

on:
  push:
    paths:
      - 'images/**'

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Process image
        env:
          IMGGO_API_KEY: ${{ secrets.IMGGO_API_KEY }}
        run: |
          cd examples/languages/curl
          ./basic-upload.sh ../../../images/invoice.jpg pat_abc123
```

### GitLab CI

```yaml
process_images:
  script:
    - export IMGGO_API_KEY=$IMGGO_API_KEY
    - cd examples/languages/curl
    - ./basic-upload.sh ../../../images/invoice.jpg pat_abc123
  only:
    - main
```

### Jenkins Pipeline

```groovy
pipeline {
  agent any
  environment {
    IMGGO_API_KEY = credentials('imggo-api-key')
  }
  stages {
    stage('Process') {
      steps {
        sh '''
          cd examples/languages/curl
          ./basic-upload.sh ../../../images/invoice.jpg pat_abc123
        '''
      }
    }
  }
}
```

### Cron Job

```bash
# Process images every hour
0 * * * * cd /path/to/examples/languages/curl && ./basic-upload.sh /data/invoice.jpg pat_abc123 >> /var/log/imggo.log 2>&1
```

## Batch Processing with Shell

Process multiple images:

```bash
#!/bin/bash

PATTERN_ID="pat_abc123"
IMAGE_DIR="/path/to/images"

for image in "$IMAGE_DIR"/*.jpg; do
  echo "Processing: $image"
  ./basic-upload.sh "$image" "$PATTERN_ID"

  if [ $? -eq 0 ]; then
    echo "Success: $image"
  else
    echo "Failed: $image" >> failures.log
  fi
done

echo "Batch processing complete"
```

## Common Issues

### Issue: `Permission denied`

**Solution:**

```bash
chmod +x *.sh
```

### Issue: `IMGGO_API_KEY: not found`

**Solution:**

```bash
export IMGGO_API_KEY="your_key_here"
```

Or check your environment:

```bash
echo $IMGGO_API_KEY
```

### Issue: `curl: command not found`

**Solution (Ubuntu/Debian):**

```bash
sudo apt-get install curl
```

**Solution (macOS):**

```bash
brew install curl
```

### Issue: `Bad file descriptor` or `sed: RE error`

**Cause:** Shell compatibility issues (sh vs bash)

**Solution:** Make sure to use bash:

```bash
#!/bin/bash
# (not #!/bin/sh)
```

### Issue: Script hangs indefinitely

**Cause:** No timeout set

**Solution:** Add timeout to curl:

```bash
curl --max-time 30 "URL"
```

### Issue: `jq: command not found`

**Note:** These examples don't require `jq`. They use `grep`, `sed`, and `cut` which are standard Unix tools.

If you prefer `jq`:

```bash
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS

# Then use:
JOB_ID=$(echo "$RESPONSE" | jq -r '.data.job_id')
```

## Advanced Examples

### Parallel Processing with GNU Parallel

```bash
# Install GNU parallel
sudo apt-get install parallel

# Process images in parallel (4 concurrent)
find images/ -name "*.jpg" | \
  parallel -j 4 ./basic-upload.sh {} pat_abc123
```

### Save Results to File

```bash
#!/bin/bash

RESULT=$(./basic-upload.sh image.jpg pat_abc123)
echo "$RESULT" > output.json

echo "Result saved to output.json"
```

### Integration with Other Tools

```bash
# Upload, process, then send to webhook
RESULT=$(./basic-upload.sh image.jpg pat_abc123)

curl -X POST "https://my-webhook.com/results" \
  -H "Content-Type: application/json" \
  -d "$RESULT"
```

## Next Steps

- See [Use Cases](../../../use-cases/) for complete end-to-end examples
- See [Formats](../../formats/) for output format examples
- See [Integrations](../../../integrations/) for database/automation setup

## Need Help?

- [API Reference](../../../docs/api-reference/)
- [Getting Started Guide](../../../docs/getting-started/)
- GitHub Issues
