#!/bin/bash

# URL Processing Example
#
# Process images from public URLs (S3, CDN, cloud storage, etc.)
#
# Usage:
#   ./url-processing.sh <image_url> PATTERN_ID
#
# Example:
#   ./url-processing.sh https://my-cdn.com/invoices/inv001.jpg pat_invoice_abc123

set -e

# Check arguments
if [ $# -ne 2 ]; then
  echo "Usage: ./url-processing.sh <image_url> <pattern_id>"
  exit 1
fi

IMAGE_URL="$1"
PATTERN_ID="$2"

# Check API key
if [ -z "$IMGGO_API_KEY" ]; then
  echo "Error: IMGGO_API_KEY environment variable not set"
  echo "Please run: export IMGGO_API_KEY=\"your_api_key_here\""
  exit 1
fi

# Validate URL format
if [[ ! "$IMAGE_URL" =~ ^https?:// ]]; then
  echo "Error: Image URL must start with http:// or https://"
  exit 1
fi

IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

echo "Processing URL: $IMAGE_URL"
echo ""

# Step 1: Submit URL for processing
echo "Submitting URL..."
UPLOAD_RESPONSE=$(curl -s -X POST \
  "$IMGGO_BASE_URL/patterns/$PATTERN_ID/ingest" \
  -H "Authorization: Bearer $IMGGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"image_url\": \"$IMAGE_URL\"}")

# Check for errors
if echo "$UPLOAD_RESPONSE" | grep -q '"error"'; then
  echo "Request failed:"
  echo "$UPLOAD_RESPONSE" | grep -o '"error":"[^"]*"'
  exit 1
fi

# Extract job_id
JOB_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
  echo "Error: Failed to extract job_id from response"
  echo "$UPLOAD_RESPONSE"
  exit 1
fi

echo "Job created: $JOB_ID"
echo ""

# Step 2: Poll for results
echo "Waiting for processing..."
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT + 1))

  # Get job status
  JOB_RESPONSE=$(curl -s -X GET \
    "$IMGGO_BASE_URL/jobs/$JOB_ID" \
    -H "Authorization: Bearer $IMGGO_API_KEY")

  # Extract status
  STATUS=$(echo "$JOB_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

  echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS: $STATUS"

  # Check if succeeded
  if [ "$STATUS" = "succeeded" ]; then
    echo ""
    echo "============================================================"
    echo "EXTRACTED DATA"
    echo "============================================================"

    # Extract manifest or result (simple extraction for demonstration)
    if echo "$JOB_RESPONSE" | grep -q '"manifest"'; then
      echo "$JOB_RESPONSE" | grep -o '"manifest":{[^}]*}' | sed 's/"manifest"://'
    elif echo "$JOB_RESPONSE" | grep -q '"result"'; then
      echo "$JOB_RESPONSE" | grep -o '"result":{[^}]*}' | sed 's/"result"://'
    else
      echo "$JOB_RESPONSE"
    fi

    echo ""
    exit 0
  fi

  # Check if failed
  if [ "$STATUS" = "failed" ]; then
    echo ""
    echo "Job failed:"
    echo "$JOB_RESPONSE" | grep -o '"error":"[^"]*"'
    exit 1
  fi

  # Wait before next attempt
  sleep 2
done

echo ""
echo "Error: Job timeout after $MAX_ATTEMPTS attempts"
exit 1
