#!/bin/bash

# Error Handling Example
#
# Production-ready curl example with comprehensive error handling:
# - Automatic retry with exponential backoff
# - Rate limit handling (429)
# - HTTP status code checking
# - Idempotency keys
#
# Usage:
#   ./error-handling.sh path/to/image.jpg PATTERN_ID
#
# Example:
#   ./error-handling.sh ../../test-images/invoice1.jpg pat_invoice_abc123

set -e

# Configuration
MAX_RETRIES=3
MAX_POLL_ATTEMPTS=60

# Check arguments
if [ $# -ne 2 ]; then
  echo "Usage: ./error-handling.sh <image_path> <pattern_id>"
  exit 1
fi

IMAGE_PATH="$1"
PATTERN_ID="$2"

# Check API key
if [ -z "$IMGGO_API_KEY" ]; then
  echo "Error: IMGGO_API_KEY environment variable not set"
  echo "Please run: export IMGGO_API_KEY=\"your_api_key_here\""
  exit 1
fi

# Check if image file exists
if [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: Image file not found: $IMAGE_PATH"
  exit 1
fi

IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

# Generate idempotency key (prevents duplicate uploads)
IDEMPOTENCY_KEY="upload-$(basename "$IMAGE_PATH")-$PATTERN_ID-$(date +%s)"

echo "Processing: $IMAGE_PATH"
echo "Idempotency Key: $IDEMPOTENCY_KEY"
echo ""

# Function: Upload with retry
upload_with_retry() {
  local retry=0

  while [ $retry -lt $MAX_RETRIES ]; do
    retry=$((retry + 1))
    echo "Upload attempt $retry/$MAX_RETRIES..." >&2

    # Make request and capture both response and HTTP code
    HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
      "$IMGGO_BASE_URL/patterns/$PATTERN_ID/ingest" \
      -H "Authorization: Bearer $IMGGO_API_KEY" \
      -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
      -F "image=@$IMAGE_PATH")

    # Split response body and status code
    HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
    HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)

    echo "  HTTP Status: $HTTP_CODE" >&2

    # Success (200-299)
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
      JOB_ID=$(echo "$HTTP_BODY" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

      if [ -z "$JOB_ID" ]; then
        echo "  Error: Failed to extract job_id" >&2
        return 1
      fi

      echo "  Job created: $JOB_ID" >&2
      echo "$JOB_ID"
      return 0
    fi

    # Rate limit (429)
    if [ "$HTTP_CODE" -eq 429 ]; then
      RETRY_AFTER=$(echo "$HTTP_RESPONSE" | grep -i "retry-after:" | awk '{print $2}')
      RETRY_AFTER=${RETRY_AFTER:-60}

      echo "  Rate limited. Waiting $RETRY_AFTER seconds..." >&2

      if [ $retry -lt $MAX_RETRIES ]; then
        sleep "$RETRY_AFTER"
        continue
      else
        echo "  Error: Rate limit exceeded after $MAX_RETRIES attempts" >&2
        return 1
      fi
    fi

    # Client errors (400-499) - don't retry
    if [ "$HTTP_CODE" -ge 400 ] && [ "$HTTP_CODE" -lt 500 ]; then
      echo "  Client error ($HTTP_CODE):" >&2
      echo "$HTTP_BODY" | grep -o '"error":"[^"]*"' || echo "$HTTP_BODY" >&2
      return 1
    fi

    # Server errors (500-599) - retry with exponential backoff
    if [ "$HTTP_CODE" -ge 500 ] && [ "$HTTP_CODE" -lt 600 ]; then
      echo "  Server error ($HTTP_CODE). Retrying..." >&2

      if [ $retry -lt $MAX_RETRIES ]; then
        WAIT_TIME=$((2 ** (retry - 1)))
        echo "  Waiting $WAIT_TIME seconds before retry..." >&2
        sleep $WAIT_TIME
        continue
      else
        echo "  Error: Server error after $MAX_RETRIES attempts" >&2
        return 1
      fi
    fi

    # Unknown error
    echo "  Unexpected HTTP status: $HTTP_CODE" >&2
    if [ $retry -lt $MAX_RETRIES ]; then
      WAIT_TIME=$((2 ** (retry - 1)))
      sleep $WAIT_TIME
      continue
    else
      return 1
    fi
  done

  return 1
}

# Function: Poll job with retry
poll_job() {
  local job_id="$1"
  local attempt=0

  echo ""
  echo "Waiting for processing..."

  while [ $attempt -lt $MAX_POLL_ATTEMPTS ]; do
    attempt=$((attempt + 1))

    # Get job status with error handling
    HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
      "$IMGGO_BASE_URL/jobs/$job_id" \
      -H "Authorization: Bearer $IMGGO_API_KEY")

    HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
    HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)

    # Handle HTTP errors during polling
    if [ "$HTTP_CODE" -ne 200 ]; then
      echo "  Polling error (HTTP $HTTP_CODE), retrying..."
      sleep 2
      continue
    fi

    # Extract status
    STATUS=$(echo "$HTTP_BODY" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    echo "  Attempt $attempt/$MAX_POLL_ATTEMPTS: $STATUS"

    # Success
    if [ "$STATUS" = "succeeded" ]; then
      echo ""
      echo "============================================================"
      echo "EXTRACTED DATA"
      echo "============================================================"

      # Extract result (same logic as basic-upload.sh)
      if echo "$HTTP_BODY" | grep -q '"manifest"'; then
        echo "$HTTP_BODY" | grep -o '"manifest":{[^}]*}' | sed 's/"manifest"://'
      elif echo "$HTTP_BODY" | grep -q '"result"'; then
        echo "$HTTP_BODY" | grep -o '"result":{[^}]*}' | sed 's/"result"://'
      else
        echo "$HTTP_BODY"
      fi

      echo ""
      return 0
    fi

    # Failed
    if [ "$STATUS" = "failed" ]; then
      echo ""
      echo "Job failed:"
      echo "$HTTP_BODY" | grep -o '"error":"[^"]*"'
      return 1
    fi

    # Still processing
    sleep 2
  done

  echo ""
  echo "Error: Job timeout after $MAX_POLL_ATTEMPTS attempts"
  return 1
}

# Main execution
echo "Step 1: Uploading image with retry logic..."
JOB_ID=$(upload_with_retry)

if [ -z "$JOB_ID" ]; then
  echo ""
  echo "Upload failed after all retries"
  exit 1
fi

echo ""
echo "Step 2: Polling for results..."
if poll_job "$JOB_ID"; then
  exit 0
else
  exit 1
fi
