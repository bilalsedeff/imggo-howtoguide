#!/bin/bash

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
PARKING_PATTERN_ID="${PARKING_PATTERN_ID}"

echo "============================================================"
echo "TESTING PARKING MANAGEMENT PATTERN"
echo "============================================================"

if [ -z "$IMGGO_API_KEY" ] || [ -z "$PARKING_PATTERN_ID" ]; then
    echo "X Error: IMGGO_API_KEY or PARKING_PATTERN_ID not set"
    exit 1
fi

TEST_IMAGE="../../test-images/parking1.jpg"
if [ ! -f "$TEST_IMAGE" ]; then
    echo "X Error: Test image not found"
    exit 1
fi

echo ""
echo "Pattern ID: ${PARKING_PATTERN_ID}"
echo "Test Image: parking1.jpg"
echo ""
echo "Processing parking image..."

INGEST_RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns/${PARKING_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -F "image=@${TEST_IMAGE}")

JOB_ID=$(echo "$INGEST_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "X Error: Failed to create job"
    exit 1
fi

echo "V Job created: ${JOB_ID}"

MAX_ATTEMPTS=60
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    sleep 2
    JOB_RESPONSE=$(curl -s -X GET "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")
    STATUS=$(echo "$JOB_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "completed" ]; then
        echo "V Processing completed!"
        echo ""

        RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"manifest":"\([^"]*\)".*/\1/p')
        if [ -z "$RESULT" ]; then
            RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p')
        fi

        mkdir -p outputs
        echo "$RESULT" | sed 's/\\n/\n/g' | sed 's/\\"/"/g' > outputs/parking1_output.xml

        echo "V Output saved to: outputs/parking1_output.xml"
        echo ""
        echo "============================================================"
        echo "EXTRACTED DATA (first 500 chars)"
        echo "============================================================"
        echo "$RESULT" | sed 's/\\n/\n/g' | head -c 500
        echo ""
        echo "..."
        echo ""
        echo "V Test completed successfully!"
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        echo "X Error: Job failed"
        exit 1
    fi

    echo "Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: Status = ${STATUS}"
    ATTEMPT=$((ATTEMPT + 1))
done

echo "X Error: Timeout"
exit 1
