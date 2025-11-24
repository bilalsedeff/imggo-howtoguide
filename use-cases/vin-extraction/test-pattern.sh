#!/bin/bash

# Simple VIN Extraction Test
# Test the pattern with a sample VIN image

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
VIN_PATTERN_ID="${VIN_PATTERN_ID}"

echo "============================================================"
echo "TESTING VIN EXTRACTION PATTERN"
echo "============================================================"

if [ -z "$IMGGO_API_KEY" ]; then
    echo ""
    echo "X Error: IMGGO_API_KEY not set"
    echo "Please set your API key in .env file"
    exit 1
fi

if [ -z "$VIN_PATTERN_ID" ]; then
    echo ""
    echo "X Error: VIN_PATTERN_ID not set"
    echo "Run create-pattern.sh first to create a pattern"
    exit 1
fi

TEST_IMAGE="../../test-images/vin1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo ""
    echo "X Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo ""
echo "Pattern ID: ${VIN_PATTERN_ID}"
echo "Test Image: vin1.jpg"
echo ""

# Upload and process image
echo "Processing VIN image..."

INGEST_RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns/${VIN_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -F "image=@${TEST_IMAGE}")

JOB_ID=$(echo "$INGEST_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "X Error: Failed to create job"
    echo "$INGEST_RESPONSE"
    exit 1
fi

echo "V Job created: ${JOB_ID}"

# Poll for completion
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

        # Extract result
        RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"manifest":"\([^"]*\)".*/\1/p')
        if [ -z "$RESULT" ]; then
            RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p')
        fi

        # Save to outputs folder
        mkdir -p outputs
        echo "$RESULT" | sed 's/\\n/\n/g' | sed 's/\\"/"/g' > outputs/vin1_output.json

        echo "V Output saved to: outputs/vin1_output.json"
        echo ""

        # Display result
        echo "============================================================"
        echo "EXTRACTED VIN DATA"
        echo "============================================================"
        echo "$RESULT" | sed 's/\\n/\n/g' | sed 's/\\"/"/g'
        echo ""

        echo "V Test completed successfully!"
        exit 0

    elif [ "$STATUS" = "failed" ]; then
        echo "X Error: Job failed"
        echo "$JOB_RESPONSE"
        exit 1
    fi

    echo "Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: Status = ${STATUS}"
    ATTEMPT=$((ATTEMPT + 1))
done

echo "X Error: Timeout waiting for job completion"
exit 1
