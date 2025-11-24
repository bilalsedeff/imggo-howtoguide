#!/bin/bash

# ImgGo XML Output - curl Example
# Process images and get XML results

set -e

IMGGO_BASE_URL="https://img-go.com/api"
IMGGO_API_KEY="${IMGGO_API_KEY}"
PARKING_PATTERN_ID="${PARKING_PATTERN_ID:-pat_parking_xml}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required"
    exit 1
fi

echo "========================================"
echo "ImgGo XML Extraction - curl Example"
echo "========================================"

TEST_IMAGE="../../test-images/parking1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo -e "\nProcessing: $TEST_IMAGE"

IDEMPOTENCY_KEY="xml-curl-$(date +%s)"

# Upload image
UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${PARKING_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "image=@${TEST_IMAGE}")

JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    exit 1
fi

echo "Job ID: $JOB_ID"

# Poll for result
echo -e "\nPolling for XML result..."

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

        # Extract XML result
        RESULT=$(echo "$JOB_RESPONSE" | jq -r '.data.result')

        echo -e "\nExtracted XML:"
        echo "======================================"
        echo "$RESULT"

        # Save to file
        OUTPUT_FILE="parking_result.xml"
        echo "$RESULT" > "$OUTPUT_FILE"
        echo -e "\n✓ Saved to $OUTPUT_FILE"

        # Validate XML if xmllint is available
        if command -v xmllint &> /dev/null; then
            echo -e "\nValidating XML..."
            if echo "$RESULT" | xmllint --noout - 2>/dev/null; then
                echo "✓ XML is well-formed"
            else
                echo "⚠ XML validation warning (may still be usable)"
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
