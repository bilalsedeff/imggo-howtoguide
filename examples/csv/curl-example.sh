#!/bin/bash

# ImgGo CSV Output - curl Example
# Process images and get CSV results using bash/curl

set -e

# Configuration
IMGGO_BASE_URL="https://img-go.com/api"
IMGGO_API_KEY="${IMGGO_API_KEY}"
INVENTORY_PATTERN_ID="${INVENTORY_PATTERN_ID:-pat_inventory_csv}"

# Check requirements
if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

echo "========================================"
echo "ImgGo CSV Extraction - curl Example"
echo "========================================"

# Find test image
TEST_IMAGE="../../test-images/inventory1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo -e "\nProcessing: $TEST_IMAGE"

# Generate idempotency key
IDEMPOTENCY_KEY="csv-curl-$(date +%s)"

# Step 1: Upload image
echo -e "\nStep 1: Uploading image..."

UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${INVENTORY_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "file=@${TEST_IMAGE}")

JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    exit 1
fi

echo "Job ID: $JOB_ID"

# Step 2: Poll for result
echo -e "\nStep 2: Polling for CSV result..."

MAX_ATTEMPTS=30
WAIT_SECONDS=2
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS..."

    JOB_RESPONSE=$(curl -s -X GET \
        "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")

    STATUS=$(echo "$JOB_RESPONSE" | jq -r '.data.status')

    if [ "$STATUS" = "completed" ]; then
        echo -e "\n✓ Processing completed!"

        # Extract CSV result
        RESULT=$(echo "$JOB_RESPONSE" | jq -r '.data.result')

        echo -e "\nExtracted CSV Data:"
        echo "======================================"
        echo "$RESULT"

        # Save to file
        OUTPUT_FILE="inventory_result.csv"
        echo "$RESULT" > "$OUTPUT_FILE"
        echo -e "\n✓ Saved to $OUTPUT_FILE"

        # Count rows
        ROW_COUNT=$(($(echo "$RESULT" | wc -l) - 1))  # Subtract header
        echo -e "\nTotal items: $ROW_COUNT"

        # Display first 5 rows
        echo -e "\nFirst 5 items:"
        echo "$RESULT" | head -6

        exit 0

    elif [ "$STATUS" = "failed" ]; then
        echo -e "\n✗ Processing failed"
        ERROR=$(echo "$JOB_RESPONSE" | jq -r '.data.error // "Unknown error"')
        echo "Error: $ERROR"
        exit 1
    else
        sleep $WAIT_SECONDS
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo -e "\n✗ Timeout"
exit 1
