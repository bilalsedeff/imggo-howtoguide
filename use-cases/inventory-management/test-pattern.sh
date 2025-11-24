#!/bin/bash

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
INVENTORY_PATTERN_ID="${INVENTORY_PATTERN_ID}"

echo "============================================================"
echo "TESTING INVENTORY MANAGEMENT PATTERN"
echo "============================================================"

if [ -z "$IMGGO_API_KEY" ] || [ -z "$INVENTORY_PATTERN_ID" ]; then
    echo "X Error: Required environment variables not set"
    exit 1
fi

TEST_IMAGE="../../test-images/inventory1.jpg"
if [ ! -f "$TEST_IMAGE" ]; then
    echo "X Error: Test image not found"
    exit 1
fi

echo ""
echo "Processing inventory image..."

INGEST_RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns/${INVENTORY_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -F "image=@${TEST_IMAGE}")

JOB_ID=$(echo "$INGEST_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "X Error: Failed to create job"
    exit 1
fi

MAX_ATTEMPTS=60
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    sleep 2
    JOB_RESPONSE=$(curl -s -X GET "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")
    STATUS=$(echo "$JOB_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "completed" ]; then
        RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"manifest":"\([^"]*\)".*/\1/p')
        if [ -z "$RESULT" ]; then
            RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p')
        fi

        mkdir -p outputs
        echo "$RESULT" | sed 's/\\n/\n/g' > outputs/inventory1_output.csv

        echo "V Output saved to: outputs/inventory1_output.csv"
        echo ""
        echo "============================================================"
        echo "EXTRACTED CSV DATA"
        echo "============================================================"
        echo "$RESULT" | sed 's/\\n/\n/g'
        echo ""
        echo "V Test completed successfully!"
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        echo "X Error: Job failed"
        exit 1
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

echo "X Error: Timeout"
exit 1
