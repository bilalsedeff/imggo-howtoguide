#!/bin/bash

# ImgGo YAML Output - curl Example
# Process images and get YAML results

set -e

IMGGO_BASE_URL="https://img-go.com/api"
IMGGO_API_KEY="${IMGGO_API_KEY}"
CONSTRUCTION_PATTERN_ID="${CONSTRUCTION_PATTERN_ID:-pat_construction_yaml}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required"
    exit 1
fi

echo "========================================"
echo "ImgGo YAML Extraction - curl Example"
echo "========================================"

IMAGE_URL="https://example.com/construction-site.jpg"

echo -e "\nProcessing construction image from URL: $IMAGE_URL"

IDEMPOTENCY_KEY="yaml-curl-$(date +%s)"

# Submit URL for processing
UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${CONSTRUCTION_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -d "{\"image_url\": \"${IMAGE_URL}\"}")

JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    exit 1
fi

echo "Job ID: $JOB_ID"

# Poll for result
echo -e "\nPolling for YAML result..."

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

        # Extract YAML result
        RESULT=$(echo "$JOB_RESPONSE" | jq -r '.data.result')

        echo -e "\nExtracted YAML:"
        echo "======================================"
        echo "$RESULT"

        # Save to file
        OUTPUT_FILE="construction_progress.yaml"
        echo "$RESULT" > "$OUTPUT_FILE"
        echo -e "\n✓ Saved to $OUTPUT_FILE"

        # Validate YAML if yq is available
        if command -v yq &> /dev/null; then
            echo -e "\nValidating YAML..."
            if echo "$RESULT" | yq eval '.' - > /dev/null 2>&1; then
                echo "✓ YAML is valid"
            else
                echo "⚠ YAML validation warning"
            fi
        fi

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
